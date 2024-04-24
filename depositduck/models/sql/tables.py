"""
Gather all table models here to simplify importing
only table models in the alembic `env` module.

(c) 2024 Alberto Morón Hernández
"""

# ruff: noqa: F401
from depositduck.models.sql.auth import AccessToken, User  # pragma: no cover
from depositduck.models.sql.email import Email  # pragma: no cover
from depositduck.models.sql.llm import (  # pragma: no cover
    EmbeddingNomic,
    Snippet,
    SourceText,
)
from depositduck.models.sql.people import Prospect  # pragma: no cover
