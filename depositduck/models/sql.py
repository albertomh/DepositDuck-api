"""
SQLModel classes to define base models and database tables.
Where only tables are required for SQLModel / Alembic, import the `tables` package, which
re-exports the table models defined here.

(c) 2024 Alberto Morón Hernández
"""

from sqlmodel import Field, SQLModel


class PersonBase(SQLModel):
    name: str
    family_name: str


class Person(PersonBase, table=True):
    id: int = Field(default=None, primary_key=True)
