"""
(c) 2024 Alberto Morón Hernández
"""

import uuid

from fastapi_users import schemas
from pydantic import BaseModel


class UserBase(BaseModel):
    first_name: str | None = None
    family_name: str | None = None
    # TODO: add audit fields to complement fastapi-users' `is_active`, `is_verified`
    #       ie. `activated_at`, `verified_at`

class UserRead(UserBase, schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(UserBase, schemas.BaseUserCreate):
    # compulsory `email` & `password` fields
    confirm_password: str


class UserUpdate(UserBase, schemas.BaseUserUpdate):
    # optional `password` field
    pass
