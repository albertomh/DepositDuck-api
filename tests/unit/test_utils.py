"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, datetime

import pytest

from depositduck.utils import (
    date_from_iso8601_str,
    days_since_date,
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
    result = await date_from_iso8601_str("2024/04/22")

    assert result is None


@pytest.mark.asyncio
async def test_days_since_date_past():
    current_year = datetime.today().year
    last_year = current_year - 1
    input_date = date(last_year, 1, 1)

    result = await days_since_date(input_date)

    assert result >= 0


@pytest.mark.asyncio
async def test_days_since_date_future():
    current_year = datetime.today().year
    next_year = current_year + 1
    input_date = date(next_year, 1, 1)

    result = await days_since_date(input_date)

    assert result < 0


@pytest.mark.asyncio
async def test_days_since_date_today():
    input_date = datetime.today().date()

    result = await days_since_date(input_date)

    assert result == 0
