"""
(c) 2024 Alberto Morón Hernández
"""

import unittest.mock

import pytest

from depositduck.main import get_llmapp
from tests.unit.conftest import get_aclient

# TODO


@pytest.mark.asyncio
async def test_docs_inaccessible_when_debug_false():
    with unittest.mock.patch("depositduck.dependables.get_settings") as mock_get_settings:
        mock_get_settings.return_value.debug = True
        llmapp = get_llmapp()

    web_client = await get_aclient(llmapp, "http://llmtest")
    async with web_client as client:
        response = await client.get("/docs")
        assert response.status_code == 404
