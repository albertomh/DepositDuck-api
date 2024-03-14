"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import Depends, FastAPI
from typing_extensions import Annotated

from depositduck import config
from depositduck.dependencies import get_settings

app = FastAPI()


@app.get("/")
async def root(settings: Annotated[config.Settings, Depends(get_settings)]):
    return {"name": settings.app_name}
