"""
UserManager and related dependables using fastapi-users.
https://fastapi-users.github.io/fastapi-users/13.0/configuration/user-manager/

(c) 2024 Alberto Morón Hernández
"""

import uuid
from enum import Enum
from typing import Annotated, Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlmodel.access_token import SQLModelAccessTokenDatabaseAsync
from sqlalchemy.ext.asyncio import AsyncSession

from depositduck.dependables import get_db_session, get_logger, get_settings
from depositduck.models.sql.auth import AccessToken, User

settings = get_settings()
LOG = get_logger()
ACCESS_TOKEN_LIFETIME_IN_SECONDS = 3600


class InvalidPasswordReason(str, Enum):
    PASSWORD_TOO_SHORT = "PASSWORD_TOO_SHORT"  # nosec B105


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    # reset & verification token lifetimes default to 3600 seconds
    reset_password_token_secret = settings.app_secret
    verification_token_secret = settings.app_secret

    async def validate_password(
        self,
        password: str,
        user: User,  # type: ignore
    ) -> None:
        # TODO: stub - validate length & check isn't common password
        if len(password) < 8:
            raise InvalidPasswordException(
                reason=InvalidPasswordReason.PASSWORD_TOO_SHORT
            )

    async def on_after_register(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        LOG.debug(f"User {user.id} registered")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        # TODO: stub - save event for analytics
        LOG.debug(f"User {user.id} logged in")

    async def on_after_request_verify(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        # TODO: stub - enqueue verification email
        LOG.debug(f"Verification requested for user {user.id} - token: {token}")

    async def on_after_forgot_password(
        self,
        user: User,
        token: str,
        request: Optional[Request] = None,
    ):
        # TODO: stub - rate limit & enqueue reset email
        LOG.debug(f"User {user.id} requested a password reset - token: {token}")

    async def on_after_reset_password(
        self,
        user: User,
        request: Optional[Request] = None,
    ):
        # TODO: stub - log
        LOG.debug(f"User {user.id} has reset their password.")


async def get_user_db(db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    yield SQLAlchemyUserDatabase(db_session, User)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
):
    yield UserManager(user_db)


async def get_access_token_db(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
):
    yield SQLModelAccessTokenDatabaseAsync(db_session, AccessToken)


def get_database_strategy(
    access_token_db: Annotated[
        AccessTokenDatabase[AccessToken], Depends(get_access_token_db)
    ],
) -> DatabaseStrategy:
    return DatabaseStrategy(
        access_token_db, lifetime_seconds=ACCESS_TOKEN_LIFETIME_IN_SECONDS
    )
