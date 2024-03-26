"""
(c) 2024 Alberto Morón Hernández
"""

import pytest

from depositduck.settings import AvailableLLM, Settings


def test_valid_llm_settings(monkeypatch):
    monkeypatch.setenv("LLM__EMBEDDING_MODEL_NAME", "multi-qa-MiniLM-L6-cos-v1")

    settings = Settings()

    minilm = AvailableLLM.MULTI_QA_MINILM_L6_COS_V1
    assert settings.llm.embedding_model.value.name == minilm.value.name
    assert settings.llm.embedding_model.value.dimensions == minilm.value.dimensions


def test_missing_llm_model_name(monkeypatch):
    invalid_model_name = ""
    monkeypatch.setenv("LLM__EMBEDDING_MODEL_NAME", invalid_model_name)

    with pytest.raises(ValueError) as exc_info:
        Settings()

    msg = f"no AvailableLLM found matching 'embedding_model_name={invalid_model_name}"
    assert msg in str(exc_info)
