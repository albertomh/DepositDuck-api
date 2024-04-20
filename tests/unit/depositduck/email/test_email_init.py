"""
(c) 2024 Alberto Morón Hernández
"""

from smtplib import SMTP
from unittest.mock import Mock, patch

import pytest

from depositduck.email import record_email, send_email
from depositduck.settings import Settings
from tests.unit.conftest import get_valid_settings

SENDER = "sender@example.com"
RECIPIENT = "recipient@example.com"
SUBJECT = "Test Subject"
HTML_BODY = "<p>Hello, world!</p>"


@pytest.mark.asyncio
async def test_record_email(mock_async_sessionmaker, mock_async_session):
    await record_email(
        mock_async_sessionmaker,
        SENDER,
        RECIPIENT,
        SUBJECT,
        HTML_BODY,
    )

    mock_async_session.add.assert_called_once()
    db_session_call_args = mock_async_session.add.call_args[0][0]
    assert db_session_call_args.sender_address == SENDER
    assert db_session_call_args.recipient_address == RECIPIENT
    assert db_session_call_args.subject == SUBJECT
    assert db_session_call_args.body == HTML_BODY
    assert db_session_call_args.sent_at is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("use_ssl", [False, True])
async def test_send_email(monkeypatch, mock_async_sessionmaker, use_ssl):
    settings_data = get_valid_settings().model_dump()
    settings_data["smtp_use_ssl"] = use_ssl
    settings = Settings(**settings_data)

    smtp_patch_loc = "depositduck.email.SMTP_SSL" if use_ssl else "depositduck.email.SMTP"
    with (
        patch(smtp_patch_loc) as mock_SMTP,
        patch("depositduck.email.record_email") as mock_record_email,
    ):
        mock_SMTP_server = Mock(spec=SMTP)
        mock_SMTP.return_value.__enter__.return_value = mock_SMTP_server
        await send_email(
            settings,
            mock_async_sessionmaker,
            RECIPIENT,
            SUBJECT,
            HTML_BODY,
        )

        if use_ssl:
            mock_SMTP.assert_called_once()
            smtp_call_args = mock_SMTP.call_args_list[0][0]
            assert smtp_call_args[0] == settings.smtp_server
            assert smtp_call_args[1] == settings.smtp_port
            mock_SMTP_server.starttls.assert_called_once()
            mock_SMTP_server.login.assert_called_once_with(
                settings.smtp_sender_address,
                settings.smtp_password,
            )
        else:
            mock_SMTP.assert_called_once_with(
                settings.smtp_server,
                settings.smtp_port,
            )
            mock_SMTP_server.starttls.assert_not_called()
            mock_SMTP_server.login.assert_not_called()
        mock_SMTP_server.sendmail.assert_called_once()
        sendmail_args = mock_SMTP_server.sendmail.call_args_list[0][0]
        assert sendmail_args[0] == settings.smtp_sender_address
        assert sendmail_args[1] == RECIPIENT
        assert HTML_BODY in sendmail_args[2]
        mock_record_email.assert_called_once_with(
            mock_async_sessionmaker,
            settings.smtp_sender_address,
            RECIPIENT,
            SUBJECT,
            HTML_BODY,
        )
        mock_SMTP_server.quit.assert_called_once()
