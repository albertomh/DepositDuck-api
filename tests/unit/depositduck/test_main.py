"""
(c) 2024 Alberto Morón Hernández
"""

import unittest.mock

import pytest
from starlette.routing import Mount

from depositduck.main import get_llmapp, get_webapp, webapp
from tests.unit.conftest import get_aclient


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
async def test_web_docs_inaccessible_when_debug_false():
    with unittest.mock.patch("depositduck.dependables.get_settings") as mock_get_settings:
        mock_get_settings.return_value.debug = True
        webapp = get_webapp()

    web_client = await get_aclient(webapp, "http://webtest")
    async with web_client as client:
        response = await client.get("/docs")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_llm_docs_inaccessible_when_debug_false():
    with unittest.mock.patch("depositduck.dependables.get_settings") as mock_get_settings:
        mock_get_settings.return_value.debug = True
        llmapp = get_llmapp()

    llm_client = await get_aclient(llmapp, "http://llmtest")
    async with llm_client as client:
        response = await client.get("/docs")
        assert response.status_code == 404
