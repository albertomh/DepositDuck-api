"""
(c) 2024 Alberto Morón Hernández
"""

import pytest


@pytest.mark.asyncio
async def test_api_root(api_client):
    response = await api_client.get("/")
    assert response.status_code == 200
    # TODO
