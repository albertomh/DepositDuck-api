"""
FastAPI routes for `webapp`, which serves DepositDuck's frontend.
Responsible for RESTful responses (in the original sense) thanks
to returning template snippets ready to be consumed by `htmx`.

(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from jinja2_fragments.fastapi import Jinja2Blocks
from typing_extensions import Annotated

from depositduck.auth.users import current_active_user
from depositduck.dependables import get_settings, get_templates
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
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {
        "app_name": settings.app_name,
        "request": request,
    }
    return templates.TemplateResponse("home.html.jinja2", context)


# TODO: decide whether to build frontend as independent fragments eg. below would be used
# as `<div hx-get="/navbar/" hx-swap="outerHTML" hx-trigger="load"></div>`
# instead of `{% include "/common/_header.html.jinja2" %}` in _base.html.jinja2
#
# @web_router.get("/navbar/", tags=["frontend"])
# async def get_navbar(
#     templates: Annotated[Jinja2Blocks, Depends(get_templates)],
#     user: Annotated[User, Depends(current_active_user)],
#     request: Request,
# ):
#     context = dict(request=request, user=user)
#     return templates.TemplateResponse("common/_navbar.html.jinja2", context=context)


@web_router.get("/motd/", tags=["kitchensink"])
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


@web_router.get("/fragment/", tags=["kitchensink"])
async def get_fragment(
    templates: Annotated[Jinja2Blocks, Depends(get_templates)],
    request: Request,
):
    context = {"request": request, "content": "✨ async load via HTMX"}
    return templates.TemplateResponse("fragments/fragment.html.jinja2", context=context)
