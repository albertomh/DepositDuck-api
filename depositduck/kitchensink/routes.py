"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from jinja2_fragments.fastapi import Jinja2Blocks
from typing_extensions import Annotated

from depositduck.auth.users import current_active_user
from depositduck.dependables import get_templates
from depositduck.models.sql.auth import User

kitchensink_router = APIRouter(prefix="/kitchensink", tags=["kitchensink"])


@kitchensink_router.get("/motd/", description="TODO: remove")
async def get_motd(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    user: Annotated[User, Depends(current_active_user)],
    request: Request,
):
    motd = "👋 hello"
    if user:
        motd += f" {user.email}!"

    context = dict(request=request, motd=motd)
    return templates.TemplateResponse(
        "home.html.jinja2", context=context, block_name="motd"
    )


@kitchensink_router.get("/fragment/", description="TODO: remove")
async def get_fragment(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {"request": request, "content": "✨ async load via HTMX"}
    return templates.TemplateResponse("fragments/fragment.html.jinja2", context=context)
