"""
FastAPI routes for `webapp`, which serves DepositDuck's frontend.
Responsible for RESTful responses (in the original sense) thanks
to returning template snippets ready to be consumed by `htmx`.

(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated

from depositduck.auth.users import current_active_user
from depositduck.dependables import AuthenticatedJinjaBlocks, get_settings, get_templates
from depositduck.models.sql.auth import User
from depositduck.settings import Settings

web_router = APIRouter()


@web_router.get(
    "/",
    summary="[htmx]",
    tags=["frontend"],
)
async def root(
    settings: Annotated[Settings, Depends(get_settings)],
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        app_name=settings.app_name,
    )
    return templates.TemplateResponse("home.html.jinja2", context)
