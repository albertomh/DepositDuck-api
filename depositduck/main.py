"""
(c) 2024 Alberto Morón Hernández
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from depositduck import VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH
from depositduck.api.routes import api_router
from depositduck.db import init_db
from depositduck.dependables import get_db_engine, get_settings
from depositduck.web.routes import web_router

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
settings = get_settings()


@asynccontextmanager
async def webapp_lifespan(app: FastAPI):
    db_engine = get_db_engine(settings)
    await init_db(db_engine)

    yield


def get_webapp() -> FastAPI:
    webapp = FastAPI(
        title=f"{settings.app_name} webapp",
        description="",
        version=VERSION,
        debug=settings.debug,
        openapi_url="/openapi.json" if settings.debug else None,
        default_response_class=HTMLResponse,
        lifespan=webapp_lifespan,
    )
    static_dir_by_package = [("depositduck.web", "static")]
    webapp.mount("/static", StaticFiles(packages=static_dir_by_package), name="static")
    return webapp


def get_apiapp() -> FastAPI:
    apiapp = FastAPI(
        title=f"{settings.app_name} apiapp",
        description="",
        version=VERSION,
        debug=settings.debug,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    return apiapp


webapp = get_webapp()
webapp.include_router(web_router)

apiapp = get_apiapp()
webapp.mount("/api", apiapp)
apiapp.include_router(api_router)
