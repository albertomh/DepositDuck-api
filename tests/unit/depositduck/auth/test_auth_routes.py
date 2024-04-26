"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime

import pytest
from fastapi import status

from depositduck.auth.routes import register


@pytest.mark.asyncio
async def test_register_happy_path(
    mock_async_sessionmaker,
    mock_async_session,
    mock_authenticated_jinja_blocks,
    mock_user_manager,
    mock_user,
    mock_request,
):
    """
    Check the happy path to create a new user:
      - validates and saves their email & password
      - sets the correct flags on their User
      - creates a bare-bones Tenancy object linked to the user
      - redirects the user to the login screen with the necessary query param
    """
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
