"""
(c) 2024 Alberto Morón Hernández
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.deposit import TenancyBase

if TYPE_CHECKING:
    from depositduck.models.sql.auth import User


class Tenancy(TenancyBase, TableBase, table=True):
    __tablename__ = "deposit__tenancy"

    user_id: UUID = Field(foreign_key="auth__user.id")

    user: "User" = Relationship(back_populates="tenancy")

    def __str__(self) -> str:
        return f"Tenancy[{self.id}]"
