"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from depositduck import config
from depositduck.dependencies import get_settings

web_router = APIRouter()


@web_router.get("/")
async def root(
    settings: Annotated[config.Settings, Depends(get_settings)],
):
    return f"app: {settings.app_name}"
