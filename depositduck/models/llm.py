"""
Base models for LLM functionality.

(c) 2024 Alberto Morón Hernández
"""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, PositiveInt


class SourceTextBase(BaseModel):
    """
    A text that we wish to use in Retrieval-Augmented Generation, in its entirety.
    """

    name: str
    filename: str | None = None
    url: str | None = None
    description: str
    content: str


class SnippetBase(BaseModel):
    """
    A small amount of text of a size suitable for use to generate an embedding
    or include in the context window of an LLM prompt.
    """

    content: str
    source_text_id: UUID


class LLMBase(BaseModel):
    """
    Metadata about a Large Language Model.
    """

    # `name` is a tag from the ollama model library: https://ollama.com/library
    name: str
    dimensions: PositiveInt


class AvailableLLM(Enum):
    """
    The source of truth for LLMs available now or used previously.
    """

    # https://www.sbert.net/docs/pretrained_models.html
    MINILM_L6_V2 = LLMBase(name="all-minilm:l6-v2", dimensions=384)
    MULTI_QA_MINILM_L6_COS_V1 = LLMBase(name="multi-qa-MiniLM-L6-cos-v1", dimensions=384)


class EmbeddingBase(BaseModel):
    """
    All embedding models & tables must inherit from this one
    for SQLAlchemy ORM mapping to work.
    """

    snippet_id: UUID
    llm_name: str
    vector: list[float]


class EmbeddingMiniLML6V2Base(EmbeddingBase):
    """
    An embedding generated using the 'all-minilm:l6-v2' model.
    All-round model tuned for many use-cases.
    https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
    """


class EmbeddingMiniLML6MultiQABase(EmbeddingBase):
    """
    An embedding generated using the 'multi-qa-MiniLM-L6-cos-v1'  model.
    Model tuned for semantic search.
    https://huggingface.co/sentence-transformers/multi-qa-MiniLM-L6-cos-v1
    """
