"""
FastAPI application entrypoint.
Defines two apps: `webapp` and `apiapp`. The first is the main app
and entrypoint, with the latter mounted on the former under `/api`.

Point compatible ASGI servers (eg. uvicorn) to `webapp` in this module.

(c) 2024 Alberto Morón Hernández
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from depositduck import VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH
from depositduck.api.routes import api_router
from depositduck.auth.routes import auth_router
from depositduck.dependables import get_db_engine, get_settings
from depositduck.llm.routes import llm_router
from depositduck.web.routes import web_router

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
settings = get_settings()
db_engine = get_db_engine(settings)


def get_webapp() -> FastAPI:
    webapp = FastAPI(
        title=f"🦆 {settings.app_name} webapp",
        description="",
        version=VERSION,
        debug=settings.debug,
        openapi_url="/openapi.json" if settings.debug else None,
        default_response_class=HTMLResponse,
    )
    static_dir_by_package = [("depositduck.web", "static")]
    webapp.mount("/static", StaticFiles(packages=static_dir_by_package), name="static")  # type: ignore[arg-type]
    return webapp


def get_apiapp() -> FastAPI:
    apiapp = FastAPI(
        title=f"⚙️ {settings.app_name} apiapp",
        description="",
        version=VERSION,
        debug=settings.debug,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    return apiapp


def get_llmapp() -> FastAPI:
    llmapp = FastAPI(
        title=f"🤖 {settings.app_name} llmapp",
        description="",
        version=VERSION,
        debug=settings.debug,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    return llmapp


webapp = get_webapp()
webapp.include_router(web_router)
webapp.include_router(auth_router)

apiapp = get_apiapp()
webapp.mount("/api", apiapp)
apiapp.include_router(api_router)

llmapp = get_llmapp()
webapp.mount("/llm", llmapp)
llmapp.include_router(llm_router)
