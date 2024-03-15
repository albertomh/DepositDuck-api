"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated

from depositduck import config
from depositduck.dependencies import get_settings, get_templates

web_router = APIRouter()


@web_router.get("/")
async def root(
    settings: Annotated[config.Settings, Depends(get_settings)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    request: Request,
):
    context = {"app_name": settings.app_name}
    return templates.TemplateResponse(
        request=request, name="main.html.jinja2", context=context
    )
