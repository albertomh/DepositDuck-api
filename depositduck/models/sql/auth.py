"""
(c) 2024 Alberto Morón Hernández
"""

from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from pydantic import EmailStr
from sqlmodel import AutoString, Field

from depositduck.models.auth import UserBase
from depositduck.models.common import CreatedAtMixin, DeletedAtMixin


class User(DeletedAtMixin, CreatedAtMixin, SQLModelBaseUserDB, UserBase, table=True):
    __tablename__ = "auth__user"

    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)
