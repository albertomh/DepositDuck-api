"""
(c) 2024 Alberto Morón Hernández
"""

import unittest.mock

import pytest

from depositduck.main import get_webapp
from tests.conftest import get_aclient


@pytest.mark.asyncio
async def test_web_root(web_client):
    response = await web_client.get("/")
    assert response.status_code == 200
    # TODO


@pytest.mark.asyncio
async def test_docs_inaccessible_when_debug_false():
    with unittest.mock.patch("depositduck.dependables.get_settings") as mock_get_settings:
        mock_get_settings.return_value.debug = True
        webapp = get_webapp()

    web_client = await get_aclient(webapp, "http://webtest")
    async with web_client as client:
        response = await client.get("/docs")
        assert response.status_code == 404
