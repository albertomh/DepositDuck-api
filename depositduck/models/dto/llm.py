"""
Data Transfer Objects for LLM-related functionality. Lightweight wrappers around
the core <X>Base Pydantic objects which define the fields for each model.

(c) 2024 Alberto Morón Hernández
"""

from depositduck.models.llm import SourceTextBase


class SourceTextCreate(SourceTextBase):
    pass
