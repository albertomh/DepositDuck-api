"""
Database tables to keep track of which LLMs are in use and store embeddings.

(c) 2024 Alberto Morón Hernández
"""

from sqlmodel import Field, SQLModel

from depositduck.models.common import CreatedAtMixin, DeletedAtMixin
from depositduck.models.llm import LLMBase


class LLM(LLMBase, CreatedAtMixin, DeletedAtMixin, SQLModel, table=True):
    """
    The source of truth for LLMs available or previously used is the AvailableLLM enum.
    We must keep track of these LLM options in the database in order to eg. link
    embeddings to the model used to generate them.
    """

    __tablename__ = "llm__llm"

    name: str = Field(primary_key=True)
