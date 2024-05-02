from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Request
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from depositduck.auth.dependables import (
    InvalidPasswordException,
    InvalidPasswordReason,
    User,
    UserCreate,
    UserManager,
)


@pytest.fixture
def user_manager():
    mock_user_db = Mock(spec=SQLAlchemyUserDatabase)
    return UserManager(mock_user_db)


@pytest.mark.asyncio
async def test_validate_password_too_short(user_manager):
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.validate_password("pass")

    assert exc_info.value.reason == InvalidPasswordReason.PASSWORD_TOO_SHORT


@pytest.mark.asyncio
async def test_create_invalid_password(user_manager):
    user_create = UserCreate(
        email="test@example.com",
        password="password",
        confirm_password="different_password",
    )
    with pytest.raises(InvalidPasswordException) as exc_info:
        await user_manager.create(user_create)

    assert exc_info.value.reason == InvalidPasswordReason.CONFIRM_PASSWORD_DOES_NOT_MATCH


# TODO: on_after_register


# TODO: on_after_login


# TODO: on_after_register


@pytest.mark.asyncio
async def test_on_after_request_verify(user_manager):
    user = User(id=1)
    token = "verification_token"
    request = AsyncMock(spec=Request)

    with patch(
        "depositduck.auth.dependables.send_verification_email"
    ) as mock_send_verification_email:
        await user_manager.on_after_request_verify(user, token, request)

    mock_send_verification_email.assert_called_once_with(user, token)


@pytest.mark.asyncio
async def test_on_after_verify(user_manager):
    user = User(id=1, verified_at=None)
    current_time = datetime.now()

    mock_db_update = AsyncMock()
    user_manager.user_db.update = mock_db_update
    with patch("depositduck.auth.dependables.datetime") as mock_datetime:
        mock_datetime.now.return_value = current_time
        await user_manager.on_after_verify(user)

    mock_db_update.assert_awaited_once()
    assert mock_db_update.await_args[0][1]["verified_at"] == current_time


# TODO: on_after_forgot_password


# TODO: on_after_reset_password
