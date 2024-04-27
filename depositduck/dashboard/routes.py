"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated

from depositduck.auth.users import current_active_user
from depositduck.dependables import AuthenticatedJinjaBlocks, get_logger, get_templates
from depositduck.middleware import frontend_auth_middleware
from depositduck.models.sql.auth import User

dashboard_frontend_router = APIRouter(
    dependencies=[Depends(frontend_auth_middleware)],
    tags=["dashboard", "frontend"],
)
dashboard_operations_router = APIRouter(prefix="/dashboard", tags=["dashboard"])

LOG = get_logger()


@dashboard_frontend_router.get(
    "/welcome/",
    summary="[htmx]",
)
async def onboarding(
    templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    context = AuthenticatedJinjaBlocks.TemplateContext(
        request=request,
        user=user,
        classes_by_id={},
    )
    return templates.TemplateResponse("dashboard/onboarding.html.jinja2", context)
