"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import EmailStr
from typing_extensions import Annotated

from depositduck.auth.users import current_active_user
from depositduck.dependables import AuthenticatedJinjaBlocks, get_templates
from depositduck.email import render_html_email, send_email
from depositduck.models.email import HtmlEmail
from depositduck.models.sql.auth import User

kitchensink_router = APIRouter(prefix="/kitchensink", tags=["kitchensink"])


@kitchensink_router.post("/send_email/")
async def send_test_email(
    recipient: EmailStr,
):
    subject = "Kitchensink test"
    context = HtmlEmail(
        title=subject,
        preheader="Kitchensink test email from local development.",
    )
    html: str = await render_html_email("please_verify.html.jinja2", context)
    await send_email(recipient, subject, html)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@kitchensink_router.get("/motd/", description="TODO: remove")
async def get_motd(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    motd = "👋 hello"
    if user:
        motd += f" {user.email}!"

    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        motd=motd,
    )
    return templates.TemplateResponse(
        "home.html.jinja2", context=context, block_name="motd"
    )


@kitchensink_router.get("/fragment/", description="TODO: remove")
async def get_fragment(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        content="✨ async load via HTMX",
    )
    return templates.TemplateResponse("fragments/fragment.html.jinja2", context=context)
