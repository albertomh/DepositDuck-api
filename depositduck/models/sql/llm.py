"""
Database tables to keep track of which LLMs are in use and store embeddings.

(c) 2024 Alberto Morón Hernández
"""

from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel

from depositduck.models.common import CreatedAtMixin, DeletedAtMixin, IdMixin, TableBase
from depositduck.models.llm import (
    AvailableLLM,
    EmbeddingMiniLML6V2Base,
    LLMBase,
    SnippetBase,
    SourceTextBase,
)


class SourceText(SourceTextBase, TableBase, table=True):
    __tablename__ = "llm__source_text"


class Snippet(SnippetBase, TableBase, table=True):
    __tablename__ = "llm__snippet"

    source_text_id: UUID = Field(default=None, foreign_key="llm__source_text.id")
    source_text: SourceText = Relationship(back_populates="snippets")


class LLM(SQLModel, LLMBase, CreatedAtMixin, DeletedAtMixin, table=True):
    """
    The source of truth for LLMs available now or used previously is the AvailableLLM
    enum. We must keep track of these LLM options in the database in order to
    eg. link embeddings to the model used to generate them.
    """

    __tablename__ = "llm__llm"

    name: str = Field(primary_key=True)


# Each LLM has a different number of dimensions, so we need
# to store the embeddings generated by each in separate
# tables that have an appropriately-sized vector column.


class EmbeddingMiniLML6V2(
    SQLModel, EmbeddingMiniLML6V2Base, IdMixin, CreatedAtMixin, table=True
):
    __tablename__ = "llm__embedding_minilm_l6_v2"

    vector: list[float] = Field(
        sa_column=Column(
            Vector(AvailableLLM.MINILM_L6_V2.value.dimensions), nullable=False
        )
    )
    llm_id: str = Field(default=None, foreign_key="llm__llm.name")
    llm: LLM = Relationship(back_populates="embeddings")
