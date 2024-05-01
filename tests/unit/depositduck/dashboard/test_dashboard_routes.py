"""
(c) 2024 Alberto Morón Hernández
"""

from typing import Any, Iterator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import status

from depositduck.dashboard.routes import (
    AsyncSession,
    current_active_user,
    db_session_factory,
)
from depositduck.models.sql.deposit import Tenancy


class AwaitableMock(AsyncMock):
    def __await__(self) -> Iterator[Any]:
        self.await_count += 1
        return iter([])


@pytest.mark.asyncio
async def test_onboarding_route_allows_user_with_null_completed_onboarding_at(
    web_client_factory,
    mock_user,
    mock_async_sessionmaker,
):
    mock_user.completed_onboarding_at = None
    dependency_overrides = {
        current_active_user: lambda: mock_user,
        db_session_factory: lambda: mock_async_sessionmaker,
    }
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    with patch.object(AsyncSession, "execute", AsyncMock) as mock_execute:
        mock_tenancy = Mock(spec=Tenancy)
        mock_scalar_one = Mock(return_value=mock_tenancy)
        mock_result = AsyncMock()
        mock_result.scalar_one = mock_scalar_one
        mock_execute.return_value = mock_result

        async with web_client as client:
            response = await client.get("/welcome/")

    assert response.status_code == status.HTTP_200_OK
    assert response.next_request is None
    mock_async_sessionmaker.begin.assert_called_once()
    mock_result.scalar_one.assert_called_once()
