"""
Database tables to keep track of which LLMs are in use and store embeddings.

(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.email import EmailBase
from depositduck.models.sql.auth import User


class Email(EmailBase, TableBase, table=True):
    __tablename__ = "email__email"

    recipient_id: UUID = Field(nullable=True, default=None, foreign_key="auth__user.id")
    sent_at: datetime = Field(nullable=True, default=None)

    user: User = Relationship(back_populates="emails")
