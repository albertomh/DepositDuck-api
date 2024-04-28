"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import date, datetime, timedelta

from cryptography.fernet import Fernet
from fastapi import Response, status


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
    """
    Raises:
        cryptography.fernet.InvalidToken
    """
    token_bytes: bytes = encrypted_token.encode()
    decrypted_bytes: bytes = _get_fernet(secret_key).decrypt(token_bytes)
    return decrypted_bytes.decode()


async def date_from_iso8601_str(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"invalid date format: {date_str}")
        return None


async def days_since_date(target_date: date) -> int:
    """
    Positive for dates in the past.
    Zero for today.
    Negative for future dates.
    """
    today = datetime.today().date()
    delta: timedelta = today - target_date
    return delta.days


async def htmx_redirect_to(redirect_to: str) -> Response:
    headers = {"HX-Redirect": redirect_to}
    response = Response(status_code=status.HTTP_303_SEE_OTHER, headers=headers)
    return response
