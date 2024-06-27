"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException, Request, status

from depositduck.dashboard.routes import AsyncSession, db_session_factory
from depositduck.middleware import (
    FRONTEND_MUST_BE_LOGGED_OUT_PATHS,
    _get_path_from_request,
    _redirect,
    current_active_user,
)
from depositduck.models.sql.auth import User
from depositduck.models.sql.deposit import Tenancy
from tests.unit.conftest import mock_user


def test_redirect_no_query_string():
    redirect_path = "/some/path"
    query_str = None

    with pytest.raises(HTTPException) as exc_info:
        _redirect(redirect_path, query_str)

    assert exc_info.value.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert exc_info.value.headers["Location"] == redirect_path


@pytest.mark.parametrize(
    "redirect_path, query_str",
    [
        ("/some/path/", "param1=value1&param2=value2"),
        ("/some/path/?existing_param=123", "param1=value1&param2=value2"),
        ("/some/path/?another=param", "?foo=bar"),
    ],
)
def test_redirect_with_query_string(redirect_path, query_str):
    with pytest.raises(HTTPException) as exc_info:
        _redirect(redirect_path, query_str)

    query_str = query_str[1:] if query_str.startswith("?") else query_str
    expected_location = f"{redirect_path}?{query_str}"
    assert exc_info.value.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert exc_info.value.headers["Location"] == expected_location


@pytest.mark.asyncio
async def test_get_path_from_request_no_query():
    mock_request = AsyncMock(spec=Request)
    mock_request.base_url = "http://example.com"
    path = "/login/"
    mock_request.url = f"http://example.com{path}"

    result = await _get_path_from_request(mock_request)

    expected_result = (path, None)
    assert result == expected_result


@pytest.mark.asyncio
async def test_get_path_from_request_with_query():
    mock_request = AsyncMock(spec=Request)
    mock_request.base_url = "http://example.com"
    path = "/user/"
    query = "id=123&next=/path/"
    mock_request.url = f"http://example.com{path}?{query}"

    result = await _get_path_from_request(mock_request)

    expected_result = (path, query)
    assert result == expected_result


# ---- if user is None and path not in FRONTEND_MUST_BE_LOGGED_OUT_PATHS:


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
    "target_path, query_params",
    [
        ("/welcome/", ""),
        ("/", "query=param"),
    ],
)
async def test_protected_routes_next_path_and_params_are_in_redirect(
    web_client_factory, target_path, query_params
):
    dependency_overrides = {current_active_user: lambda: None}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )
    expected_next_path = f"/login/?next={target_path}"
    if query_params:
        target_path += f"?{query_params}"
        expected_next_path += f"&{query_params}"

    async with web_client as client:
        response = await client.get(target_path)

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        next_path = response.next_request.url.raw_path.decode()
        assert next_path == expected_next_path


# ---- if user is not None and path in FRONTEND_MUST_BE_LOGGED_OUT_PATHS


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


# ---- if user is not None and user.completed_onboarding_at is ...


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "completed_onboarding_at, http_status, redirect_to",
    [
        (None, status.HTTP_307_TEMPORARY_REDIRECT, "/welcome/"),
        (datetime.now(), status.HTTP_200_OK, None),
    ],
)
async def test_protected_routes_redirects_user_to_onboarding(
    web_client_factory,
    mock_user,
    mock_async_sessionmaker,
    completed_onboarding_at,
    http_status,
    redirect_to,
):
    mock_user.completed_onboarding_at = completed_onboarding_at
    dependency_overrides = {
        current_active_user: lambda: mock_user,
        db_session_factory: lambda: mock_async_sessionmaker,
    }
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )
    with patch.object(AsyncSession, "execute", AsyncMock) as mock_execute:
        mock_scalar_one = Mock(return_value=Tenancy(deposit_in_p=10000, end_date=None))
        mock_result = AsyncMock()
        mock_result.scalar_one = mock_scalar_one
        mock_execute.return_value = mock_result

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == http_status
    if redirect_to is None:
        assert response.next_request is None
    else:
        assert response.next_request.url.path == redirect_to


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
async def test_onboarding_route_redirects_already_onboarded_user(
    web_client_factory, mock_user, mock_async_sessionmaker, mock_async_session
):
    mock_user.completed_onboarding_at = datetime.now()
    dependency_overrides = {
        current_active_user: lambda: mock_user,
        db_session_factory: lambda: mock_async_sessionmaker,
    }
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get("/welcome/")

    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.next_request.url.path == "/"
    mock_async_sessionmaker.begin.assert_not_called()


# ----- not caught by the conditionals in the middleware

# All routes are protected by default, with exceptions made for those in
# FRONTEND_MUST_BE_LOGGED_OUT_PATHS.


@pytest.mark.asyncio
async def test_protected_routes_accept_user(web_client_factory, mock_async_sessionmaker):
    dependency_overrides = {
        current_active_user: lambda: Mock(spec=User),
        db_session_factory: lambda: mock_async_sessionmaker,
    }
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )
    with patch.object(AsyncSession, "execute", AsyncMock) as mock_execute:
        mock_scalar_one = Mock(return_value=Tenancy(deposit_in_p=10000, end_date=None))
        mock_result = AsyncMock()
        mock_result.scalar_one = mock_scalar_one
        mock_execute.return_value = mock_result

    async with web_client as client:
        response = await client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.next_request is None
