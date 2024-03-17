"""
(c) 2024 Alberto Morón Hernández
"""

import unittest.mock

import pytest

from depositduck.main import get_apiapp
from tests.conftest import get_aclient


@pytest.mark.asyncio
async def test_api_root(api_client):
    response = await api_client.get("/")
    assert response.status_code == 200
    # TODO


@pytest.mark.asyncio
async def test_docs_inaccessible_when_debug_false():
    with unittest.mock.patch("depositduck.dependables.get_settings") as mock_get_settings:
        mock_get_settings.return_value.debug = True
        apiapp = get_apiapp()

    web_client = await get_aclient(apiapp, "http://apitest")
    async with web_client as client:
        response = await client.get("/docs")
        assert response.status_code == 404
