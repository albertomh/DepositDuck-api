"""
Configure the fastapi-users library to provide an authentication backend.

Using the SQLAlchemy adapter. The auth backend uses:
- the database strategy: can be invalidated server-side & provides data for analytics.
- the cookie transport: ol' reliable, automatically managed by browsers

https://fastapi-users.github.io/fastapi-users/13.0/configuration/overview/

(c) 2024 Alberto Morón Hernández
"""

import uuid
from typing import Literal

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
)

from depositduck.auth import AUTH_COOKIE_MAX_AGE, AUTH_COOKIE_NAME
from depositduck.auth.dependables import get_database_strategy, get_user_manager
from depositduck.dependables import get_settings
from depositduck.models.sql.auth import User

settings = get_settings()

cookie_secure = not settings.debug
cookie_samesite: Literal["lax", "strict"] = "lax" if settings.debug else "strict"
cookie_httponly = not settings.debug
cookie_transport = CookieTransport(
    cookie_name=AUTH_COOKIE_NAME,
    cookie_max_age=AUTH_COOKIE_MAX_AGE,
    # TODO: set cookie_domain for hosted environments when available via Settings
    # cookie_domain=,
    cookie_secure=cookie_secure,
    cookie_httponly=cookie_httponly,  # TODO: might not be needed
    cookie_samesite=cookie_samesite,
)

auth_backend = AuthenticationBackend(
    name="db+cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# `optional` to return None instead of directly raising a HttpException.
# `active` to require that the User attempting to log in is `active` in the database.
current_active_user = fastapi_users.current_user(optional=True, active=True)
