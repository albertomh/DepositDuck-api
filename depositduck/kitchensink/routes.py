"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Response, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import async_sessionmaker
from typing_extensions import Annotated

from depositduck.dependables import (
    db_session_factory,
    get_settings,
)
from depositduck.email import render_html_email, send_email
from depositduck.models.email import HtmlEmail
from depositduck.settings import Settings

kitchensink_router = APIRouter(prefix="/kitchensink", tags=["kitchensink"])


@kitchensink_router.post("/send_email/")
async def send_test_email(
    settings: Annotated[Settings, Depends(get_settings)],
    db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
    recipient: EmailStr,
):
    subject = "Kitchensink test"
    context = HtmlEmail(
        title=subject,
        preheader="Kitchensink test email from local development.",
    )
    html_body: str = await render_html_email("please_verify.html.jinja2", context)
    await send_email(settings, db_session_factory, recipient, subject, html_body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
