"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class EmailBase(BaseModel):
    sender_address: str
    recipient_address: str
    recipient_id: UUID | None = None
    subject: str
    body: str
    sent_at: datetime | None = None
