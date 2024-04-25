"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from unittest.mock import Mock

import pytest
from fastapi import status

from depositduck.auth.routes import register
from depositduck.auth.users import current_active_user
from depositduck.models.sql.auth import User


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url, auth_user, expected_status_code, next_url_path",
    [
        ("/login/", None, status.HTTP_200_OK, None),
        ("/login/", Mock(spec=User), status.HTTP_307_TEMPORARY_REDIRECT, "/"),
        ("/signup/", None, status.HTTP_200_OK, None),
        ("/signup/", Mock(spec=User), status.HTTP_307_TEMPORARY_REDIRECT, "/"),
    ],
)
async def test_auth_routes_redirect_user_based_on_authentication(
    web_client_factory, url, auth_user, expected_status_code, next_url_path
):
    dependency_overrides = {current_active_user: lambda: auth_user}
    web_client = await web_client_factory(
        settings=None, dependency_overrides=dependency_overrides
    )

    async with web_client as client:
        response = await client.get(url)

    assert response.status_code == expected_status_code
    if auth_user:
        assert response.next_request.url.path == next_url_path
    else:
        assert response.next_request is None


@pytest.mark.asyncio
async def test_register_happy_path(
    mock_async_sessionmaker,
    mock_async_session,
    mock_authenticated_jinja_blocks,
    mock_user_manager,
    mock_user,
    mock_request,
):
    # arrange
    tenancy_end_date = datetime.now().date().strftime("%Y-%m-%d")
    email = "user@example.com"
    password, confirm_password = "password", "password"
    mock_user_manager.create.return_value = mock_user

    # act
    response = await register(
        tenancy_end_date,
        email,
        password,
        confirm_password,
        mock_async_sessionmaker,
        mock_authenticated_jinja_blocks,
        mock_user_manager,
        None,
        mock_request,
    )

    # assert
    mock_user_manager.create.assert_awaited_once()
    user_create = mock_user_manager.create.await_args[0][0]
    assert user_create.email == email
    assert user_create.password == password
    assert user_create.is_active
    assert not user_create.is_superuser
    assert not user_create.is_verified
    mock_user_manager.validate_password.assert_awaited_once()
    assert mock_user_manager.validate_password.await_args[0][0] == password
    mock_async_session.add.assert_called_once()
    new_tenancy = mock_async_session.add.call_args[0][0]
    assert new_tenancy.deposit_in_p == 0
    assert new_tenancy.end_date == tenancy_end_date
    assert new_tenancy.user_id == mock_user.id
    mock_user_manager.request_verify.assert_awaited_once()
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["hx-redirect"] == "/login/?prev=/auth/signup/"
