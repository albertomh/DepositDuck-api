"""
(c) 2024 Alberto Morón Hernández
"""

from unittest.mock import Mock, patch

import pytest

from depositduck.auth import send_verification_email
from depositduck.models.sql.auth import User


@pytest.mark.asyncio
async def test_send_verification_email():
    user_email = "user@example.com"
    mock_user = Mock(spec=User)
    mock_user.email = user_email
    token = "encrypted_token"

    with patch("depositduck.auth.send_email") as mock_send_email:
        await send_verification_email(mock_user, token)

        mock_send_email.assert_called_once()
        send_email_call_args = mock_send_email.call_args_list[0][0]
        assert send_email_call_args[2] == user_email
        assert f"&token={token}" in send_email_call_args[4]
