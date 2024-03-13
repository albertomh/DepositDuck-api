"""
(c) 2024 Alberto Morón Hernández
"""

import pytest


@pytest.mark.asyncio
async def test_main_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
