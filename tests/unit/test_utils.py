"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, datetime

import pytest

from depositduck.utils import (
    date_from_iso8601_str,
    days_between_dates,
    decrypt,
    encrypt,
    is_valid_fernet_key,
)
from tests.unit.conftest import VALID_FERNET_KEY


def test_is_valid_fernet_key_valid():
    assert is_valid_fernet_key(VALID_FERNET_KEY)


def test_is_valid_fernet_key_invalid():
    with pytest.raises((ValueError, TypeError)):
        is_valid_fernet_key("invalid_key")


def test_encrypt_decrypt_with_valid_key():
    data = "sensitive-auth-token"

    encrypted_data = encrypt(VALID_FERNET_KEY, data)
    assert encrypted_data != data

    decrypted_data = decrypt(VALID_FERNET_KEY, encrypted_data)
    assert decrypted_data == data


def test_encrypt_decrypt_invalid_key():
    invalid_secret_key = "invalid_fernet_key"
    data = "sensitive-auth-token"

    with pytest.raises(Exception):
        encrypt(invalid_secret_key, data)

    with pytest.raises(Exception):
        decrypt(invalid_secret_key, "invalid_token")


@pytest.mark.asyncio
async def test_date_from_iso8601_str_valid():
    current_year = datetime.today().year
    input_date_str = f"{current_year}-04-22"

    result = await date_from_iso8601_str(input_date_str)

    expected_date = date(current_year, 4, 22)
    assert isinstance(result, date)
    assert result == expected_date


@pytest.mark.asyncio
async def test_date_from_iso8601_str_invalid():
    date_str = "2024/04/22"

    with pytest.raises(ValueError) as exc_info:
        await date_from_iso8601_str(date_str)

    assert (
        str(exc_info.value) == f"time data '{date_str}' does not match format '%Y-%m-%d'"
    )


@pytest.mark.asyncio
async def test_days_between_dates_past():
    today = datetime.today().date()
    current_year = datetime.today().year
    last_year = current_year - 1
    input_date = date(last_year, 1, 1)

    result = days_between_dates(today, input_date)

    assert result < 0


@pytest.mark.asyncio
async def test_days_between_dates_future():
    today = datetime.today().date()
    current_year = datetime.today().year
    next_year = current_year + 1
    input_date = date(next_year, 1, 1)

    result = days_between_dates(today, input_date)

    assert result > 0


@pytest.mark.asyncio
async def test_days_between_dates_today():
    today = datetime.today().date()
    input_date = datetime.today().date()

    result = days_between_dates(today, input_date)

    assert result == 0
