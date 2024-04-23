"""
(c) 2024 Alberto Morón Hernández
"""

from uuid import UUID

from pydantic import BaseModel


class PersonBase(BaseModel):
    first_name: str
    family_name: str | None = None
    user_id: UUID
