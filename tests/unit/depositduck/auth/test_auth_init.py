"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from depositduck.auth import (
    MAX_DAYS_IN_ADVANCE,
    TDS_DISPUTE_WINDOW_IN_DAYS,
    DepositProvider,
    DisputeWindowHasClosed,
    TenancyEndTooFarAway,
    TooCloseToDisputeWindowEnd,
    is_prospect_suitable,
    send_verification_email,
)

TODAY_DATE = datetime.today().date()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_date, end_date",
    [
        (
            (datetime.today() - timedelta(days=365)).date(),
            (datetime.today() - timedelta(days=(TDS_DISPUTE_WINDOW_IN_DAYS - 10))).date(),
        ),
        ((datetime.today() - timedelta(days=365)).date(), datetime.today().date()),
    ],
)
async def test_is_prospect_suitable_happy_path(start_date, end_date):
    result = await is_prospect_suitable(DepositProvider.TDS.value, start_date, end_date)

    assert result is True


@pytest.mark.asyncio
async def test_is_prospect_suitable_not_accepted_due_to_provider():
    """
    Invalid prospect due to unsuitable provider, suitable date.
    """
    provider = "invalid_provider"
    start_date = (datetime.today() - timedelta(days=365)).date()
    end_date = datetime.today().date()

    with pytest.raises(ExceptionGroup) as exc_info:
        await is_prospect_suitable(provider, start_date, end_date)

    assert (
        str(exc_info.value.exceptions[0])
        == f"prospect unsuitable due to provider '{provider}'"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_date, end_date, expected_exc_type",
    [
        (
            (datetime.today() - timedelta(days=365)).date(),
            (datetime.today() - timedelta(days=(TDS_DISPUTE_WINDOW_IN_DAYS + 1))).date(),
            DisputeWindowHasClosed,
        ),
        (
            (datetime.today() - timedelta(days=365)).date(),
            (datetime.today() - timedelta(days=(TDS_DISPUTE_WINDOW_IN_DAYS - 3))).date(),
            TooCloseToDisputeWindowEnd,
        ),
    ],
)
async def test_is_prospect_suitable_not_accepted_due_to_outside_dispute_window(
    start_date, end_date, expected_exc_type
):
    """
    Invalid prospect due to suitable provider, today falling either:
      - outside (tenancy end date + dispute window).
      - between (dispute_window_end - 5) and dispute_window_end
    """
    with pytest.raises(ExceptionGroup) as exc_info:
        await is_prospect_suitable(DepositProvider.TDS.value, start_date, end_date)

    exc = exc_info.value.exceptions[0]
    assert isinstance(exc, expected_exc_type)


@pytest.mark.asyncio
async def test_is_prospect_suitable_not_accepted_due_to_over_six_months_away():
    """
    Invalid prospect due to suitable provider, unsuitable tenancy end date due to being
    over six_months away.
    """
    start_date = datetime.today().date()
    end_date = (datetime.today() + timedelta(days=(MAX_DAYS_IN_ADVANCE + 1))).date()

    with pytest.raises(ExceptionGroup) as exc_info:
        await is_prospect_suitable(DepositProvider.TDS.value, start_date, end_date)

    exc = exc_info.value.exceptions[0]
    assert isinstance(exc, TenancyEndTooFarAway)


@pytest.mark.asyncio
async def test_send_verification_email(mock_user):
    user_email = "user@example.com"
    mock_user.email = user_email
    token = "encrypted_token"

    with patch("depositduck.auth.send_email") as mock_send_email:
        await send_verification_email(mock_user, token)

        mock_send_email.assert_called_once()
        send_email_call_args = mock_send_email.call_args_list[0][0]
        assert send_email_call_args[2] == user_email
        assert f"&token={token}" in send_email_call_args[4]
