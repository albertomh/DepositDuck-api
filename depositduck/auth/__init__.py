"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date
from enum import Enum

from sqlalchemy.ext.asyncio import async_sessionmaker

from depositduck.dependables import db_session_factory, get_logger, get_settings
from depositduck.email import render_html_email, send_email
from depositduck.models.email import HtmlEmail
from depositduck.models.sql.auth import User
from depositduck.utils import days_since_date, encrypt

settings = get_settings()
LOG = get_logger()


class DepositProvider(str, Enum):
    OTHER = "other"
    TDS = "tds"


TDS_TIME_LIMIT_IN_DAYS = 90  # 3 months

AUTH_COOKIE_NAME = "dd_auth"
AUTH_COOKIE_MAX_AGE = 3600

VERIFICATION_EMAIL_SUBJECT = "Your DepositDuck account verification"
VERIFICATION_EMAIL_PREHEADER = (
    "Please verify your DepositDuck account - and get what's yours!"
)


async def is_prospect_acceptable(deposit_provider: str, tenancy_end_date: date) -> bool:
    """
    Determine whether a prospect can be accepted as a DepositDuck user or not, based on:
      - their deposit being held by TDS
      - today falling between their tenancy end date and TDS' time limit
    """
    provider_is_accepted = deposit_provider.lower() == DepositProvider.TDS.value
    if not provider_is_accepted:
        raise ValueError(f"prospect unacceptable due to provider '{deposit_provider}'")

    days_since_end_date = await days_since_date(tenancy_end_date)
    end_date_is_within_limit = days_since_end_date < TDS_TIME_LIMIT_IN_DAYS
    if not end_date_is_within_limit:
        raise ValueError(
            f"prospect unacceptable due to end date '{str(tenancy_end_date)}'"
        )

    return provider_is_accepted and end_date_is_within_limit


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
