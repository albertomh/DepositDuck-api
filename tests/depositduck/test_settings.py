"""
(c) 2024 Alberto Morón Hernández
"""

import pytest

from depositduck.dependables import get_settings
from depositduck.settings import AvailableLLM, Settings


def test_valid_llm_settings():
    settings = get_settings()

    minilm = AvailableLLM.MINILM_L6_V2
    assert settings.llm.embedding_model.name == minilm.value.name
    assert settings.llm.embedding_model.dimensions == minilm.value.dimensions


def test_missing_llm_model_name(monkeypatch):
    monkeypatch.setenv("LLM__EMBEDDING_MODEL_NAME", "")

    with pytest.raises(ValueError) as exc_info:
        Settings()

    assert "invalid model choice" in str(exc_info)
    assert "- check LLM__EMBEDDING_MODEL_NAME in .env" in str(exc_info)
