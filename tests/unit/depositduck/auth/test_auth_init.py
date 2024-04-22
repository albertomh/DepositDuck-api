"""
(c) 2024 Alberto Morón Hernández
"""

import operator
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest

from depositduck.auth import (
    TDS_TIME_LIMIT_IN_DAYS,
    DepositProvider,
    is_prospect_acceptable,
    send_verification_email,
)
from depositduck.models.sql.auth import User

TODAY_DATE = datetime.today().date()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "elapsed_days, operator",
    [
        (TDS_TIME_LIMIT_IN_DAYS // 2, operator.sub),
        (TDS_TIME_LIMIT_IN_DAYS // 2, operator.add),
        (-(TDS_TIME_LIMIT_IN_DAYS + 1), operator.add),
    ],
)
async def test_is_prospect_acceptable_happy_path(elapsed_days, operator):
    """
    Prospect is acceptable when their tenancy end date is:
    - in the past and within the TDS time limit
    - in the future
    """
    mock_tenancy_end_date = operator(TODAY_DATE, timedelta(days=elapsed_days))
    days_since_date_mock = AsyncMock()
    days_since_date_mock.return_value = elapsed_days

    with patch("depositduck.auth.days_since_date", days_since_date_mock):
        result = await is_prospect_acceptable(
            DepositProvider.TDS.value, mock_tenancy_end_date
        )

        assert result is True
        days_since_date_mock.assert_called_once_with(mock_tenancy_end_date)


@pytest.mark.asyncio
async def test_is_prospect_acceptable_not_accepted_due_to_provider():
    """
    Invalid prospect due to unacceptable provider, acceptable date.
    """
    provider = "invalid_provider"
    elapsed_days = TDS_TIME_LIMIT_IN_DAYS // 2
    mock_tenancy_end_date = TODAY_DATE - timedelta(days=elapsed_days)
    days_since_date_mock = AsyncMock()
    days_since_date_mock.return_value = elapsed_days

    with (
        patch("depositduck.auth.days_since_date", days_since_date_mock),
        pytest.raises(ValueError) as exc_info,
    ):
        await is_prospect_acceptable(provider, mock_tenancy_end_date)

    assert str(exc_info.value) == f"prospect unacceptable due to provider '{provider}'"


@pytest.mark.asyncio
async def test_is_prospect_acceptable_not_accepted_due_to_date_limit():
    """
    Invalid prospect due to acceptable provider, unacceptable date.
    """
    elapsed_days = TDS_TIME_LIMIT_IN_DAYS + 1
    mock_tenancy_end_date = TODAY_DATE - timedelta(days=elapsed_days)
    days_since_date_mock = AsyncMock()
    days_since_date_mock.return_value = elapsed_days

    with (
        patch("depositduck.auth.days_since_date", days_since_date_mock),
        pytest.raises(ValueError) as exc_info,
    ):
        await is_prospect_acceptable(DepositProvider.TDS.value, mock_tenancy_end_date)

    assert (
        str(exc_info.value)
        == f"prospect unacceptable due to end date '{str(mock_tenancy_end_date)}'"
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
