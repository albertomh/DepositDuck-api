"""
Database tables to keep track of which LLMs are in use and store embeddings.

(c) 2024 Alberto Morón Hernández
"""

from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, Relationship

from depositduck.models.common import TableBase
from depositduck.models.llm import (
    NOMIC,
    SnippetBase,
    SourceTextBase,
)


class SourceText(SourceTextBase, TableBase, table=True):
    __tablename__ = "llm__source_text"

    snippets: list["Snippet"] = Relationship(back_populates="source_text")


class Snippet(SnippetBase, TableBase, table=True):
    __tablename__ = "llm__snippet"

    source_text_id: UUID = Field(default=None, foreign_key="llm__source_text.id")
    source_text: SourceText = Relationship(back_populates="snippets")
    nomic_embedding: "EmbeddingNomic" = Relationship(back_populates="snippet")


class EmbeddingNomic(TableBase, table=True):
    __tablename__ = "llm__embedding_nomic"

    snippet_id: UUID = Field(default=None, foreign_key="llm__snippet.id")
    snippet: Snippet = Relationship(back_populates="nomic_embedding")
    vector: list[float] = Field(
        sa_column=Column(Vector(NOMIC.dimensions), nullable=False)
    )
