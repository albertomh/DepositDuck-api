"""
(c) 2024 Alberto Morón Hernández
"""

import pytest


@pytest.mark.asyncio
async def test_web_root(web_client):
    response = await web_client.get("/")
    assert response.status_code == 200
    # TODO:
