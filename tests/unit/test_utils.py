"""
(c) 2024 Alberto Morón Hernández
"""

import pytest

from depositduck.utils import decrypt, encrypt, is_valid_fernet_key
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
