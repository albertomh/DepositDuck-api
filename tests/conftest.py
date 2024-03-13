"""
(c) 2024 Alberto Morón Hernández
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from depositduck.main import app


@pytest_asyncio.fixture
async def client():
    aclient = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    async with aclient as client:
        yield client
