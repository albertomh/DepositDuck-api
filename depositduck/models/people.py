"""
(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PersonBase(BaseModel):
    first_name: str
    family_name: str | None = None
    user_id: UUID


class ProspectBase(BaseModel):
    email: str
    deposit_provider_name: str
    converted_at: datetime | None = None
    person_id: UUID | None = None
