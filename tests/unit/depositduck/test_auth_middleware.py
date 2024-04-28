"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import status

from depositduck.middleware import (
    FRONTEND_MUST_BE_LOGGED_OUT_PATHS,
    current_active_user,
)
from depositduck.models.sql.auth import User
from tests.unit.conftest import mock_user


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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user, http_status, redirect_to",
    [
        (None, status.HTTP_307_TEMPORARY_REDIRECT, "/login/"),
        (mock_user, status.HTTP_403_FORBIDDEN, None),
    ],
)
async def test_must_be_logged_out_routes_forbid_authenticated_user(
    web_client_factory, user, http_status, redirect_to
):
    """
    NB. this could be more unit-test-like by focusing just on the middleware behaviour,
    and ends up testing some of /auth/verify/'s logic to ensure the middleware does not
    interfere with query params for successful responses to anonymous requests.
    """
    dependency_overrides = {current_active_user: lambda: user}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )
    email = "gAAAAABmLhGjRcgFvP9TIzi9kDUDqjLsM8amV-mCQY0XWOCaLZ6HHxlJeV36WSPFLYaWIZzpVhY9kTU2oZNnm1oVL87lTpVTPKSSC1hOyP_ajp-0G6KyYls="  # noqa: E501
    query = f"?token=tokenDoesntMatterInThisTest&email={email}"
    target_path = "/auth/verify/"

    async with web_client as client:
        response = await client.get(f"{target_path}{query}")

    assert response.status_code == http_status
    if redirect_to is None:
        assert response.next_request is None
    else:
        next_path = response.next_request.url.raw_path.decode()
        assert next_path == f"/login/?prev={target_path}&email={email}"


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
