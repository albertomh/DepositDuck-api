"""
Mixins to help build base models and tables in the context-specific
modules (auth, LLM, etc.) in this package.

(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Field, SQLModel
from sqlmodel._compat import SQLModelConfig

# --- Table models -----------------------------------------------------------------------


class IdMixin:
    id: UUID = Field(
        primary_key=True,
        sa_column_kwargs=dict(server_default=func.gen_random_uuid()),
    )


class CreatedAtMixin:
    created_at: datetime = Field(  # type: ignore
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs=dict(server_default=func.now()),
    )


# TODO: created_by
# TODO: updated_at, updated_by, etc. should be inferred from an `audit` table
# updated_at: datetime | None = Field(
#     sa_column=Column(DateTime(), onupdate=func.now())
# )


class DeletedAtMixin:
    deleted_at: datetime | None = Field(sa_type=sa.DateTime(timezone=True), nullable=True)  # type: ignore


class TableBase(SQLModel, DeletedAtMixin, CreatedAtMixin, IdMixin):
    """
    Every object has two models associated with it:
        - a Pydantic class eg. `class EntityBase(BaseModel)`
        - and a SQLModel eg. `class Entity(EntityBase, TableBase, table=True)`
    By default a SQLModel table object does not carry out Pydantic field validation.
    `validate_assignment` needed for field validation to happen when an `Entity` object
    is instantiated.
    https://github.com/tiangolo/sqlmodel/issues/52
    """

    model_config = SQLModelConfig(validate_assignment=True)


# --- Request bodies ---------------------------------------------------------------------


class EntityById(BaseModel):
    id: UUID


# --- Response objects -------------------------------------------------------------------


class TwoOhOneCreatedCount(BaseModel):
    created_count: int
