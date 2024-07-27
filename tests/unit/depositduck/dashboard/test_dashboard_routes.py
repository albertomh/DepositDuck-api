"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, datetime, timezone
from typing import Any, Iterator
from unittest.mock import AsyncMock, Mock, patch

import pytest
import time_machine
from fastapi import status

from depositduck.auth.dependables import get_user_manager
from depositduck.dashboard.routes import (
    AsyncSession,
    current_active_user,
    db_session_factory,
)
from depositduck.dependables import get_templates
from depositduck.models.auth import UserUpdate
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
        mock_tenancy_end_date = datetime.today().date()
        mock_tenancy.end_date = mock_tenancy_end_date
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


@pytest.mark.asyncio
@time_machine.travel(datetime(2024, 5, 4, 19, 46, 0, tzinfo=timezone.utc), tick=False)
async def test_complete_onboarding_happy_path(
    web_client_factory,
    mock_user,
    mock_user_manager,
    mock_async_sessionmaker,
    mock_authenticated_jinja_blocks,
):
    # arrange
    mock_user.completed_onboarding_at = None
    dependency_overrides = {
        db_session_factory: lambda: mock_async_sessionmaker,
        get_templates: lambda: mock_authenticated_jinja_blocks,
        get_user_manager: lambda: mock_user_manager,
        current_active_user: lambda: mock_user,
    }
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )
    name = "TestUser"
    deposit_amount = 888
    tenancy_start_date = "2023-01-01"
    tenancy_end_date = "2024-04-30"

    with patch.object(AsyncSession, "execute", AsyncMock) as mock_execute:
        mock_existing_tenancy = Mock(spec=Tenancy)
        mock_scalar_one = Mock(return_value=mock_existing_tenancy)
        mock_result = AsyncMock()
        mock_result.scalar_one = mock_scalar_one
        mock_execute.return_value = mock_result

        # act
        async with web_client as client:
            form_data = dict(
                name=name,
                depositAmount=deposit_amount,
                tenancyStartDate=tenancy_start_date,
                tenancyEndDate=tenancy_end_date,
            )
            response = await client.post(
                "/dashboard/completeOnboarding/",
                data=form_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    # assert
    user_update = mock_user_manager.update.await_args[0][0]
    assert isinstance(user_update, UserUpdate)
    assert user_update.first_name == name
    assert user_update.completed_onboarding_at == datetime(
        2024, 5, 4, 19, 46, 0, tzinfo=timezone.utc
    )
    assert mock_existing_tenancy.deposit_in_p == deposit_amount * 100
    assert mock_existing_tenancy.start_date == date(2023, 1, 1)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["hx-redirect"] == "/?prev=/welcome/"
