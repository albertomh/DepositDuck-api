"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from starlette.routing import Mount

from depositduck.main import webapp
from depositduck.settings import Settings
from tests.unit.conftest import get_valid_settings_data


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
@pytest.mark.parametrize("debug_value, expected_status_code", [(True, 200), (False, 404)])
async def test_webapp_docs_visibility(
    web_client_factory, debug_value, expected_status_code
):
    settings_data = get_valid_settings_data()
    settings_data.update({"debug": debug_value})
    settings = Settings(**settings_data)
    web_client = await web_client_factory(settings)

    async with web_client as client:
        response = await client.get("/docs")

    assert response.status_code == expected_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("debug_value, expected_status_code", [(True, 200), (False, 404)])
async def test_app_docs_visibility(api_client_factory, debug_value, expected_status_code):
    settings_data = get_valid_settings_data()
    settings_data.update({"debug": debug_value})
    settings = Settings(**settings_data)
    api_client = await api_client_factory(settings)

    async with api_client as client:
        response = await client.get("/docs")

    assert response.status_code == expected_status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("debug_value, expected_status_code", [(True, 200), (False, 404)])
async def test_llmapp_docs_visibility(
    llm_client_factory, debug_value, expected_status_code
):
    settings_data = get_valid_settings_data()
    settings_data.update({"debug": debug_value})
    settings = Settings(**settings_data)
    llm_client = await llm_client_factory(settings)

    async with llm_client as client:
        response = await client.get("/docs")

    assert response.status_code == expected_status_code


# TODO: test kitchensink is not reachable when DEBUG=False
