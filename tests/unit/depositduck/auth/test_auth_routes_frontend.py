"""
(c) 2024 Alberto Morón Hernández
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import Response
from fastapi_users.authentication.strategy.db import DatabaseStrategy

from depositduck.auth.routes import log_user_in
from depositduck.models.sql.auth import User


@pytest.mark.asyncio
async def test_log_user_in():
    mock_token = "mock_token"
    mock_db_strategy = AsyncMock(spec=DatabaseStrategy)
    mock_db_strategy.write_token.return_value = mock_token
    mock_user = Mock(spec=User)
    mock_response = Response()

    mock_set_login_cookie = AsyncMock()
    mock_auth_backend = type(
        "AuthBackendMock",
        (),
        {
            "transport": type(
                "TransportMock", (), {"_set_login_cookie": mock_set_login_cookie}
            )
        },
    )

    with patch("depositduck.auth.routes.auth_backend", mock_auth_backend):
        await log_user_in(mock_db_strategy, mock_user, mock_response)

    mock_db_strategy.write_token.assert_called_once_with(mock_user)
    mock_set_login_cookie.assert_called_once_with(mock_response, mock_token)
