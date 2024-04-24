"""
Gather all table models here to simplify importing
only table models in the alembic `env` module.

(c) 2024 Alberto Morón Hernández
"""

# ruff: noqa: F401
from depositduck.models.sql.auth import AccessToken, User                   # pragma: no cover
from depositduck.models.sql.email import Email                              # pragma: no cover
from depositduck.models.sql.llm import EmbeddingNomic, Snippet, SourceText  # pragma: no cover
from depositduck.models.sql.people import Person, Prospect                  # pragma: no cover
