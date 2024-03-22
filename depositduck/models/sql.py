"""
SQLModel classes to define base models and database tables.
Where only tables are required for SQLModel / Alembic, import the `tables` package, which
re-exports the table models defined here.

(c) 2024 Alberto Morón Hernández
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class IdMixin(SQLModel):
    id: UUID | None = Field(
        primary_key=True,
        nullable=False,
        sa_column_kwargs=dict(server_default=func.gen_random_uuid()),
    )


class CreatedAtMixin(SQLModel):
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )


# TODO: created_by
# updated_at, updated_by, etc. should be inferred from an `audit` table
# updated_at: datetime | None = Field(
#     sa_column=Column(DateTime(timezone=True), onupdate=func.now())
# )


class DeletedAtMixin(SQLModel):
    deleted_at: datetime | None = Field(sa_column=Column(DateTime(timezone=True)))


class TableMixin(IdMixin, CreatedAtMixin, DeletedAtMixin):
    pass


# class PersonBase(SQLModel):
#     name: str
#     family_name: str
#
#
# class Person(PersonBase, TableMixin, table=True):
#     pass
