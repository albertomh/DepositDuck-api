"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import status

from depositduck.middleware import FRONTEND_MUST_BE_LOGGED_OUT_PATHS, current_active_user
from depositduck.models.sql.auth import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    FRONTEND_MUST_BE_LOGGED_OUT_PATHS,
)
async def test_unprotected_routes_accept_logged_out_user(web_client_factory, path):
    dependency_overrides = {current_active_user: lambda: None}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get(path)

    assert response.status_code == status.HTTP_200_OK
    assert response.next_request is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    FRONTEND_MUST_BE_LOGGED_OUT_PATHS,
)
async def test_unprotected_routes_redirect_logged_in_user(web_client_factory, path):
    dependency_overrides = {current_active_user: lambda: Mock(spec=User)}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get(path)

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.next_request.url.path == "/"


@pytest.mark.asyncio
async def test_protected_routes_accept_logged_out_user(web_client_factory):
    dependency_overrides = {current_active_user: lambda: Mock(spec=User)}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.next_request is None


@pytest.mark.asyncio
async def test_protected_routes_redirect_logged_out_user(web_client_factory):
    dependency_overrides = {current_active_user: lambda: None}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.next_request.url.path == "/login/"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "completed_onboarding_at, http_status, redirect_to",
    [
        (None, status.HTTP_307_TEMPORARY_REDIRECT, "/welcome/"),
        (datetime.now(), status.HTTP_200_OK, None),
    ],
)
async def test_protected_routes_redirects_user_to_onboarding(
    web_client_factory, mock_user, completed_onboarding_at, http_status, redirect_to
):
    mock_user.completed_onboarding_at = completed_onboarding_at
    dependency_overrides = {current_active_user: lambda: mock_user}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == http_status
    if redirect_to is None:
        assert response.next_request is None
    else:
        assert response.next_request.url.path == redirect_to


# TODO: add coverage for `OPERATIONS_MUST_BE_LOGGED_OUT_PATHS` and check 401 returned


@pytest.mark.asyncio
async def test_protected_routes_next_path_is_present_in_redirect(web_client_factory):
    dependency_overrides = {current_active_user: lambda: None}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    target_path = "/welcome/"
    async with web_client as client:
        response = await client.get(target_path)

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        next_path = response.next_request.url.raw_path.decode()
        assert next_path == f"/login/?next={target_path}"
