"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from depositduck.dependables import get_settings
from depositduck.settings import Settings

api_router = APIRouter()


@api_router.get("/")
async def root(settings: Annotated[Settings, Depends(get_settings)]):
    return {"app": settings.app_name}
