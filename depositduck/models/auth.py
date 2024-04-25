"""
(c) 2024 Alberto Morón Hernández
"""

import uuid
from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel


class UserBase(BaseModel):
    verified_at: datetime | None = None
    completed_onboarding_at: datetime | None = None
    first_name: str | None = None
    family_name: str | None = None


class UserRead(UserBase, schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(UserBase, schemas.BaseUserCreate):
    # compulsory `email` & `password` fields
    confirm_password: str


class UserUpdate(UserBase, schemas.BaseUserUpdate):
    # optional `password` field
    pass
