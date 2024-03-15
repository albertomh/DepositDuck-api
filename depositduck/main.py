"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from depositduck.api.routes import api_router
from depositduck.web.routes import web_router


def get_webapp() -> FastAPI:
    webapp = FastAPI()
    static_dir_by_package = [("depositduck.web", "static")]
    webapp.mount("/static", StaticFiles(packages=static_dir_by_package), name="static")
    return webapp


def get_apiapp() -> FastAPI:
    apiapp = FastAPI()
    return apiapp


webapp = get_webapp()
webapp.include_router(web_router)

apiapp = get_apiapp()
webapp.mount("/api", apiapp)
apiapp.include_router(api_router)
