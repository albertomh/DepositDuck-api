"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing_extensions import Annotated

from depositduck import config
from depositduck.dependables import get_settings, get_templates

web_router = APIRouter()


@web_router.get("/", response_class=HTMLResponse)
async def root(
    settings: Annotated[config.Settings, Depends(get_settings)],
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    request: Request,
):
    context = {
        "app_name": settings.app_name,
        "request": request,
    }
    return templates.TemplateResponse("home.html.jinja2", context)


@web_router.get("/motd", response_class=HTMLResponse)
async def get_motd(
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    request: Request,
):
    context = {"request": request, "motd": "👋 hello"}
    return templates.TemplateResponse(
        "home.html.jinja2", context=context, block_name="motd"
    )


@web_router.get("/fragment", response_class=HTMLResponse)
async def get_fragment(
    templates: Annotated[Jinja2Templates, Depends(get_templates)],
    request: Request,
):
    context = {"request": request, "content": "✨ async load via HTMX"}
    return templates.TemplateResponse("fragments/fragment.html.jinja2", context=context)
