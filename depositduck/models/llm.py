"""
Base models for LLM functionality.

(c) 2024 Alberto Morón Hernández
"""

from enum import Enum

from pydantic import BaseModel, PositiveInt


class SourceTextBase(BaseModel):
    """
    A text that we wish to use in Retrieval-Augmented Generation, in its entirety.
    """

    name: str
    filename: str | None
    url: str | None
    description: str
    content: str


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
