"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import APIRouter, Depends, Request
from typing_extensions import Annotated

from depositduck.dependables import get_settings
from depositduck.settings import Settings

llm_router = APIRouter()


@llm_router.get("/")
async def root(
    settings: Annotated[Settings, Depends(get_settings)],
    request: Request,
):
    # TODO: stub
    return {}
