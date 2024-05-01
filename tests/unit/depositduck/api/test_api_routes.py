"""
(c) 2024 Alberto Morón Hernández
"""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi import status

from depositduck.api.routes import AsyncSession
from depositduck.dependables import db_session_factory, get_speculum_client


@pytest.mark.asyncio
async def test_healthz_endpoint(api_client_factory, mock_async_sessionmaker):
    # arrange
    mock_speculum_client = AsyncMock(spec=httpx.AsyncClient)
    mock_speculum_response = Mock()
    mock_speculum_client.head.return_value.__aenter__.return_value = (
        mock_speculum_response
    )
    dependency_overrides = {
        get_speculum_client: lambda: mock_speculum_client,
        db_session_factory: lambda: mock_async_sessionmaker,
    }
    api_client = await api_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )
    with patch.object(AsyncSession, "execute", AsyncMock) as mock_execute:
        mock_scalar_one = Mock(return_value=1)
        mock_result = AsyncMock()
        mock_result.scalar_one = mock_scalar_one
        mock_execute.return_value = mock_result

        # act
        async with api_client as client:
            response = await client.get("/healthz")

    # assert
    mock_speculum_client.head.assert_awaited_once()
    assert mock_speculum_client.head.await_args[0][0] == "/css/main.min.css"

    mock_async_sessionmaker.begin.assert_called_once()
    mock_result.scalar_one.assert_called_once()

    assert response.status_code == status.HTTP_200_OK
