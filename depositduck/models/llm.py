"""
Base models for LLM functionality.

(c) 2024 Alberto Morón Hernández
"""

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
    version: str
    dimensions: PositiveInt


NOMIC = LLMBase(name="nomic-embed-text", version="v1.5", dimensions=768)


class EmbeddingBase(BaseModel):
    snippet_id: UUID
    llm_name: str
    vector: list[float]


class UserQuery(BaseModel):
    content: str
    # max related snippets to return from vector similarity search
    relatedSnippets: int = 5
