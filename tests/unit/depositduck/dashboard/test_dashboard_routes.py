"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime

import pytest
from fastapi import status

from depositduck.dashboard.routes import current_active_user


@pytest.mark.asyncio
async def test_user_pending_onboarding_is_redirected_to_onboarding_screen(
    web_client_factory,
    mock_user,
):
    mock_user.completed_onboarding_at = None
    dependency_overrides = {current_active_user: lambda: mock_user}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.next_request.url.path == "/welcome/"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "completed_onboarding_at, http_status, redirect_to",
    [
        (None, status.HTTP_200_OK, None),
        (datetime.now(), status.HTTP_307_TEMPORARY_REDIRECT, "/"),
    ],
)
async def test_onboarding_route_reacts_to_onboarding_at_timestamp(
    web_client_factory, mock_user, completed_onboarding_at, http_status, redirect_to
):
    mock_user.completed_onboarding_at = completed_onboarding_at
    dependency_overrides = {current_active_user: lambda: mock_user}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get("/welcome/")

    assert response.status_code == http_status
    if redirect_to is None:
        assert response.next_request is None
    else:
        assert response.next_request.url.path == redirect_to
