"""
Database tables to keep track of which LLMs are in use and store embeddings.

(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.email import EmailBase
from depositduck.models.sql.auth import User


class Email(EmailBase, TableBase, table=True):
    __tablename__ = "email__email"

    recipient_id: UUID = Field(nullable=True, foreign_key="auth__user.id")
    sent_at: datetime | None = Field(
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True)
    )

    user: User = Relationship(back_populates="emails")

    def __str__(self) -> str:
        return f"Email[{self.id}]"
