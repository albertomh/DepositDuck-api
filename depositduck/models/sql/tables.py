"""
Gather all table models here to simplify importing
only table models in the alembic `env` module.

(c) 2024 Alberto Morón Hernández
"""

# ruff: noqa: F401
from depositduck.models.sql.llm import LLM, EmbeddingMiniLML6V2, Snippet, SourceText
