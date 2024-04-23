"""
(c) 2024 Alberto Morón Hernández
"""

from typing import TYPE_CHECKING

from fastapi_users_db_sqlmodel import SQLModelBaseUserDB
from fastapi_users_db_sqlmodel.access_token import SQLModelBaseAccessToken
from pydantic import UUID4, EmailStr
from sqlmodel import AutoString, Field, Relationship

from depositduck.models.auth import UserBase
from depositduck.models.common import CreatedAtMixin, DeletedAtMixin
from depositduck.models.sql.people import Person

if TYPE_CHECKING:
    from depositduck.models.sql.email import Email

# NB. do not import sql.email here! Will cause circular import error. Look in tables.py
# for explanation and code updating forward refs.


class User(DeletedAtMixin, CreatedAtMixin, SQLModelBaseUserDB, UserBase, table=True):
    __tablename__ = "auth__user"

    email: EmailStr = Field(unique=True, index=True, sa_type=AutoString)

    emails: list["Email"] = Relationship(back_populates="user")
    access_tokens: list["AccessToken"] = Relationship(back_populates="user")
    person: "Person" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="user"
    )

    def __repr__(self):
        return f"User [id={self.id}]"


class AccessToken(SQLModelBaseAccessToken, table=True):
    __tablename__ = "auth__access_token"

    user_id: UUID4 = Field(foreign_key="auth__user.id", nullable=False)

    user: User = Relationship(back_populates="access_tokens")

    def __repr__(self):
        return f"AccessToken for User [id={self.user_id}]"


User.model_rebuild()
