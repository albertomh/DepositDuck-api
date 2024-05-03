"""
(c) 2024 Alberto Morón Hernández
"""

from enum import Enum

from sqlalchemy.ext.asyncio import async_sessionmaker

from depositduck.dependables import db_session_factory, get_logger, get_settings
from depositduck.email import render_html_email, send_email
from depositduck.models.email import HtmlEmail
from depositduck.models.sql.auth import User
from depositduck.utils import encrypt

settings = get_settings()
LOG = get_logger()


class DepositProvider(str, Enum):
    OTHER = "other"
    TDS = "tds"


TDS_DISPUTE_WINDOW_IN_DAYS = 90  # 3 months
MAX_DAYS_IN_ADVANCE = 180  # 6 months

AUTH_COOKIE_NAME = "dd_auth"
AUTH_COOKIE_MAX_AGE = 3600

VERIFICATION_EMAIL_SUBJECT = "Your DepositDuck account verification"
VERIFICATION_EMAIL_PREHEADER = (
    "Please verify your DepositDuck account - and get what's yours!"
)


class UnsuitableProvider(Exception):
    pass


class TenancyEndDateOutOfRange(Exception):
    pass


async def is_prospect_suitable(deposit_provider: str, days_since_end_date: int) -> bool:
    """
    Determine whether a prospect can be accepted as a DepositDuck user or not, based on:
      - their deposit being held by TDS
      - the tenancy end date is within the next 180 days
      - today falling between their tenancy end date and TDS' time limit

    Args:
        deposit_provider (str): A string representation of their deposit provider.
        days_since_end_date (int): Number of days since the tenancy ended. +ve for past,
          -ve for future, 0 for today.

    Returns:
        bool: True if the prospect is suitable to become a user

    Raises:
        UnsuitableProvider: Provider is other than TDS.
        TenancyEndDateOutOfRange: Too many days have passed since the end of the tenancy.
    """
    acceptable_providers = [DepositProvider.TDS.value]
    provider_is_accepted = deposit_provider.lower() in acceptable_providers
    if not provider_is_accepted:
        raise UnsuitableProvider(
            f"prospect unsuitable due to provider '{deposit_provider}'"
        )

    end_date_is_within_dispute_window = days_since_end_date < TDS_DISPUTE_WINDOW_IN_DAYS
    end_date_too_close_to_dispute_window_end = days_since_end_date > (
        TDS_DISPUTE_WINDOW_IN_DAYS - 5
    )
    if not end_date_is_within_dispute_window or end_date_too_close_to_dispute_window_end:
        raise TenancyEndDateOutOfRange(
            f"prospect unsuitable due to end date being {days_since_end_date} days ago"
        )

    end_date_is_within_next_six_months = days_since_end_date > (-1 * MAX_DAYS_IN_ADVANCE)
    if not end_date_is_within_next_six_months:
        raise TenancyEndDateOutOfRange(
            f"prospect unsuitable due to end date being {days_since_end_date * -1} "
            "days from now"
        )

    return provider_is_accepted and end_date_is_within_dispute_window


async def send_verification_email(user: User, token: str) -> None:
    LOG.debug(f"verification requested for {user} - token: {token}")

    encrypted_email = encrypt(settings.app_secret, user.email)
    verification_url = (
        f"{settings.app_origin}/auth/verify/?email={encrypted_email}&token={token}"
    )
    context = HtmlEmail(
        title=VERIFICATION_EMAIL_SUBJECT,
        preheader=VERIFICATION_EMAIL_PREHEADER,
        verification_url=verification_url,
    )
    html: str = await render_html_email("please_verify.html.jinja2", context)

    db_sessionmaker: async_sessionmaker = await db_session_factory()
    await send_email(
        settings, db_sessionmaker, user.email, VERIFICATION_EMAIL_SUBJECT, html
    )
