"""
Mixins to help build base models and tables in the context-specific
modules (auth, LLM, etc.) in this package.

(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class IdMixin:
    id: UUID = Field(
        primary_key=True,
        sa_column_kwargs=dict(server_default=func.gen_random_uuid()),
    )


class CreatedAtMixin:
    created_at: datetime = Field(sa_column_kwargs=dict(server_default=func.now()))


# TODO: created_by
# updated_at, updated_by, etc. should be inferred from an `audit` table
# updated_at: datetime | None = Field(
#     sa_column=Column(DateTime(), onupdate=func.now())
# )


class DeletedAtMixin:
    deleted_at: datetime | None = Field()


class TableBase(SQLModel, IdMixin, CreatedAtMixin, DeletedAtMixin):
    pass
