"""
(c) 2024 Alberto Morón Hernández
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.people import PersonBase, ProspectBase

if TYPE_CHECKING:
    from depositduck.models.sql.auth import User


class Person(PersonBase, TableBase, table=True):
    __tablename__ = "people__person"

    user_id: UUID = Field(default=None, foreign_key="auth__user.id")

    prospect: "Prospect" = Relationship(back_populates="person")
    user: "User" = Relationship(back_populates="person")


class Prospect(ProspectBase, TableBase, table=True):
    __tablename__ = "people__prospect"

    person_id: UUID = Field(nullable=True, default=None, foreign_key="people__person.id")

    person: "Person" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="prospect"
    )
