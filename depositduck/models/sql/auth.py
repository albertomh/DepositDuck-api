"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from pydantic import UUID4, EmailStr
from sqlmodel import AutoString, Field

from depositduck.models.auth import UserBase
from depositduck.models.common import CreatedAtMixin, DeletedAtMixin


class User(DeletedAtMixin, CreatedAtMixin, SQLModelBaseUserDB, UserBase, table=True):
    __tablename__ = "auth__user"

    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)


class AccessToken(SQLModelBaseAccessToken, table=True):
    __tablename__ = "auth__access_token"
    user_id: UUID4 = Field(foreign_key="auth__user.id", nullable=False)
