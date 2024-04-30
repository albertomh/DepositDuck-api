"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.people import ProspectBase

if TYPE_CHECKING:
    from depositduck.models.sql.auth import User


class Prospect(ProspectBase, TableBase, table=True):
    __tablename__ = "people__prospect"

    email: str = Field(nullable=False, unique=True, index=True)
    converted_at: datetime | None = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True)
    )
    user_id: UUID = Field(nullable=True, foreign_key="auth__user.id")

    user: "User" = Relationship(
        sa_relationship_kwargs={"uselist": False}, back_populates="prospect"
    )

    def __str__(self) -> str:
        return f"Prospect[{self.id}]"
