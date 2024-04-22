"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from depositduck.auth import (
    TDS_TIME_LIMIT_IN_DAYS,
    DepositProvider,
    TenancyEndDateOutOfRange,
    UnsuitableProvider,
    is_prospect_suitable,
    send_verification_email,
)
from depositduck.models.sql.auth import User

TODAY_DATE = datetime.today().date()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "days_since_end_date",
    [
        TDS_TIME_LIMIT_IN_DAYS - 1,
        TDS_TIME_LIMIT_IN_DAYS - (TDS_TIME_LIMIT_IN_DAYS // 2),
        0 - (TDS_TIME_LIMIT_IN_DAYS * 3),
    ],
)
async def test_is_prospect_suitable_happy_path(days_since_end_date):
    result = await is_prospect_suitable(DepositProvider.TDS.value, days_since_end_date)

    assert result is True


@pytest.mark.asyncio
async def test_is_prospect_suitable_not_accepted_due_to_provider():
    """
    Invalid prospect due to unsuitable provider, suitable date.
    """
    provider = "invalid_provider"
    days_since_end_date = TDS_TIME_LIMIT_IN_DAYS // 2

    with pytest.raises(UnsuitableProvider) as exc_info:
        await is_prospect_suitable(provider, days_since_end_date)

    assert str(exc_info.value) == f"prospect unsuitable due to provider '{provider}'"


@pytest.mark.asyncio
async def test_is_prospect_suitable_not_accepted_due_to_date_limit():
    """
    Invalid prospect due to suitable provider, unsuitable date.
    """
    days_since_end_date = TDS_TIME_LIMIT_IN_DAYS + 1

    with pytest.raises(TenancyEndDateOutOfRange) as exc_info:
        await is_prospect_suitable(DepositProvider.TDS.value, days_since_end_date)

    assert (
        str(exc_info.value)
        == f"prospect unsuitable due to end date being {days_since_end_date} days ago"
    )


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
