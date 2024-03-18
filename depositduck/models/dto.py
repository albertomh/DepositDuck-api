"""
Data Transfer Objects for models.
Base and table models are defined in the `sql` module.

(c) 2024 Alberto Morón Hernández
"""

from depositduck.models.sql import PersonBase


class PersonCreate(PersonBase):
    pass


class PersonRead(PersonBase):
    pass
