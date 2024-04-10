"""
Gather all table models here to simplify importing
only table models in the alembic `env` module.

(c) 2024 Alberto Morón Hernández
"""

# ruff: noqa: F401
from depositduck.models.sql.auth import AccessToken, User
from depositduck.models.sql.email import Email
from depositduck.models.sql.llm import EmbeddingNomic, Snippet, SourceText

# needed to avoid circular import between sql.auth & sql.email and allow us to
# define the many-to-many relationship `User.emails`
# see https://github.com/tiangolo/sqlmodel/issues/121#issuecomment-935656778
User.model_rebuild()
