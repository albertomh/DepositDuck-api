"""
(c) 2024 Alberto Morón Hernández
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import status

from depositduck.dependables import db_session_factory


@pytest.mark.asyncio
async def test_healthz_endpoint(
    api_client_factory, mock_async_sessionmaker, mock_async_session
):
    dependency_overrides = {db_session_factory: lambda: mock_async_sessionmaker}
    api_client = await api_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    with patch.object(mock_async_session, "execute", AsyncMock) as mock_execute:
        mock_scalar_one = Mock(return_value=1)
        mock_result = AsyncMock()
        mock_result.scalar_one = mock_scalar_one
        mock_execute.return_value = mock_result

        async with api_client as client:
            response = await client.get("/healthz")

            mock_async_sessionmaker.begin.assert_called_once()
            mock_result.scalar_one.assert_called_once()

        assert response.status_code == status.HTTP_200_OK
