"""
(c) 2024 Alberto Morón Hernández
"""

from sqlalchemy.ext.asyncio import async_sessionmaker

from depositduck.dependables import db_session_factory, get_logger, get_settings
from depositduck.email import render_html_email, send_email
from depositduck.models.email import HtmlEmail
from depositduck.models.sql.auth import User
from depositduck.utils import encrypt

settings = get_settings()
LOG = get_logger()

AUTH_COOKIE_NAME = "dd_auth"
AUTH_COOKIE_MAX_AGE = 3600

VERIFICATION_EMAIL_SUBJECT = "Your DepositDuck account verification"
VERIFICATION_EMAIL_PREHEADER = (
    "Please verify your DepositDuck account - and get what's yours!"
)


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
