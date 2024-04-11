"""
(c) 2024 Alberto Morón Hernández
"""

from cryptography.fernet import Fernet


def is_valid_fernet_key(candidate_key: str) -> bool:
    try:
        Fernet(candidate_key)
        return True
    except (ValueError, TypeError):
        raise


def _get_fernet(secret_key: str) -> Fernet:
    secret_bytes = secret_key.encode()
    return Fernet(secret_bytes)


def encrypt(secret_key: str, data: str) -> str:
    data_bytes: bytes = data.encode()
    encrypted_bytes: bytes = _get_fernet(secret_key).encrypt(data_bytes)
    return encrypted_bytes.decode()


def decrypt(secret_key: str, encrypted_token: str) -> str:
    token_bytes: bytes = encrypted_token.encode()
    decrypted_bytes: bytes = _get_fernet(secret_key).decrypt(token_bytes)
    return decrypted_bytes.decode()
