"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from fastapi import status


@pytest.mark.asyncio
async def test_web_root(web_client_factory):
    web_client = await web_client_factory()

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == status.HTTP_200_OK


# TODO: flesh out
