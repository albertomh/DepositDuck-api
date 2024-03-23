"""
Base models for LLM functionality.

(c) 2024 Alberto Morón Hernández
"""

from enum import Enum

from pydantic import BaseModel, PositiveInt


class LLMBase(BaseModel):
    # `name` is a tag from the ollama model library: https://ollama.com/library
    name: str
    dimensions: PositiveInt


class AvailableLLM(Enum):
    # https://www.sbert.net/docs/pretrained_models.html
    MINILM_L6_V2 = LLMBase(name="all-minilm:l6-v2", dimensions=384)
