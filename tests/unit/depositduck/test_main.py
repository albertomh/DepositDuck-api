"""
(c) 2024 Alberto Morón Hernández
"""

from typing import Iterable, cast

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.routing import Mount, Route

from depositduck.main import webapp
from depositduck.settings import Settings
from tests.unit.conftest import get_valid_settings


def test_app_mounts():
    """
    Test that mounts for the `api` & `llm` apps are present on the webapp.
    """
    mounts = {
        "apiapp": {"path": "/api", "observed": False},
        "llmapp": {"path": "/llm", "observed": False},
    }

    for route in webapp.routes:
        for k, v in mounts.items():
            if isinstance(route, Mount) and route.path == v["path"]:
                mounts[k]["observed"] = True
                break

    for k, v in mounts.items():
        assert v["observed"], f"{k} not mounted under '{v["path"]}'."


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "debug_setting, expected_status_code", [(True, 200), (False, 404)]
)
async def test_webapp_docs_visibility(
    web_client_factory, debug_setting, expected_status_code
):
    """
    Check that webapp's /docs is only visible when DEBUG=True.
    """
    settings_data = get_valid_settings().model_dump()
    settings_data["debug"] = debug_setting
    settings = Settings(**settings_data)
    web_client = await web_client_factory(settings)

    async with web_client as client:
        response = await client.get("/docs")

    assert response.status_code == expected_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("debug_setting", [True, False])
async def test_webapp_kitchensink_presence(web_client_factory, debug_setting) -> None:
    """
    Check that webapp's /kitchensink/ routes are only present when DEBUG=True.
    """
    settings_data = get_valid_settings().model_dump()
    settings_data["debug"] = debug_setting
    settings = Settings(**settings_data)
    web_client: AsyncClient = await web_client_factory(settings)

    app: FastAPI = web_client._transport.app
    paths = [r.path for r in cast(Iterable[Route], app.routes)]

    contains_kitchensink_routes = any(p.startswith("/kitchensink") for p in paths)
    assert contains_kitchensink_routes is debug_setting


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "debug_setting, expected_status_code", [(True, 200), (False, 404)]
)
async def test_api_docs_visibility(
    api_client_factory, debug_setting, expected_status_code
) -> None:
    """
    Check that apiapp's /docs is only visible when DEBUG=True.
    """
    settings_data = get_valid_settings().model_dump()
    settings_data["debug"] = debug_setting
    settings = Settings(**settings_data)
    api_client = await api_client_factory(settings)

    async with api_client as client:
        response = await client.get("/docs")

    assert response.status_code == expected_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "debug_setting, expected_status_code", [(True, 200), (False, 404)]
)
async def test_llmapp_docs_visibility(
    llm_client_factory, debug_setting, expected_status_code
):
    """
    Check that llmapp's /docs is only visible when DEBUG=True.
    """
    settings_data = get_valid_settings().model_dump()
    settings_data["debug"] = debug_setting
    settings = Settings(**settings_data)
    llm_client = await llm_client_factory(settings)

    async with llm_client as client:
        response = await client.get("/docs")

    assert response.status_code == expected_status_code
