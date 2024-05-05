"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, datetime
from enum import Enum

from sqlalchemy.ext.asyncio import async_sessionmaker

from depositduck.dependables import db_session_factory, get_logger, get_settings
from depositduck.email import render_html_email, send_email
from depositduck.models.email import HtmlEmail
from depositduck.models.sql.auth import User
from depositduck.utils import days_between_dates, encrypt

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


class DatesInWrongOrder(Exception):
    pass


class TenancyIsTooShort(Exception):
    pass


class TenancyEndDateOutOfRange(Exception):
    def __init__(self, days_since: int) -> None:
        super().__init__()
        self.days_since = days_since


class TooCloseToDisputeWindowEnd(TenancyEndDateOutOfRange):
    pass


class DisputeWindowHasClosed(TenancyEndDateOutOfRange):
    pass


class TenancyEndTooFarAway(TenancyEndDateOutOfRange):
    pass


def prospect_provider_is_acceptable(deposit_provider: str) -> bool:
    """
    Args:
        deposit_provider (str): A string representation of their deposit provider.

    Raises:
        UnsuitableProvider: Provider is other than TDS.
    """
    acceptable_providers = [DepositProvider.TDS.value]
    provider_is_accepted = deposit_provider.lower() in acceptable_providers
    if not provider_is_accepted:
        raise UnsuitableProvider(
            f"prospect unsuitable due to provider '{deposit_provider}'"
        )

    return provider_is_accepted


def prospect_tenancy_dates_are_acceptable(start_date: date, end_date: date) -> bool:
    """
    Raises:
        DatesInWrongOrder: the end date must follow the start date.
        TenancyIsTooShort: must be at least thirty days long.
    """
    if start_date > end_date:
        raise DatesInWrongOrder()
    difference = days_between_dates(start_date, end_date)
    if difference < 30:
        raise TenancyIsTooShort()
    return True


def prospect_end_date_is_acceptable(tenancy_end_date: date) -> bool:
    """
    Raises:
        DisputeWindowHasClosed: too many days have passed since the end of the tenancy.
        TooCloseToDisputeWindowEnd: end of dispute window is less than five days away.
        TenancyEndTooFarAway: tenancy ends more than six months in he future.
    """
    today = datetime.today().date()
    days_since_end_date = days_between_dates(today, tenancy_end_date)

    if days_since_end_date < 0:
        if (-1 * days_since_end_date) > TDS_DISPUTE_WINDOW_IN_DAYS:
            raise DisputeWindowHasClosed(days_since_end_date)
        if (-1 * days_since_end_date) > (TDS_DISPUTE_WINDOW_IN_DAYS - 5):
            raise TooCloseToDisputeWindowEnd(days_since_end_date)

    else:
        if days_since_end_date > MAX_DAYS_IN_ADVANCE:
            raise TenancyEndTooFarAway(days_since_end_date)

    return True


async def is_prospect_suitable(
    deposit_provider: str, start_date: date | None, end_date: date
) -> bool:
    """
    Determine whether a prospect can be accepted as a DepositDuck user.

    Args:
        deposit_provider (str): A string representation of their deposit provider.
        start_date (date | None):
        end_date (date):

    Returns:
        bool: True if the prospect is suitable to become a user

    Raises:
        ExceptionGroup[UnsuitableProvider, TenancyEndDateOutOfRange]
    """
    exceptions: list[Exception] = []

    try:
        provider_is_ok = prospect_provider_is_acceptable(deposit_provider)
    except UnsuitableProvider as e:
        exceptions.append(e)

    if start_date:
        try:
            dates_are_ok = prospect_tenancy_dates_are_acceptable(start_date, end_date)
        except (DatesInWrongOrder, TenancyIsTooShort) as e:
            exceptions.append(e)

    try:
        end_date_is_ok = prospect_end_date_is_acceptable(end_date)
    except (
        DisputeWindowHasClosed,
        TooCloseToDisputeWindowEnd,
        TenancyEndTooFarAway,
    ) as e:
        exceptions.append(e)

    if exceptions:
        raise ExceptionGroup("", exceptions)
    return provider_is_ok and dates_are_ok and end_date_is_ok


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
