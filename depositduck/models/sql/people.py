"""
(c) 2024 Alberto Morón Hernández
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.people import PersonBase
if TYPE_CHECKING:
    from depositduck.models.sql.auth import User


class Person(PersonBase, TableBase, table=True):
    __tablename__ = "people__person"

    user_id: UUID = Field(default=None, foreign_key="auth__user.id")

    user: "User" = Relationship(back_populates="user")
