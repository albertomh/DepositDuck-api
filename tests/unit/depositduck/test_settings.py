"""
(c) 2024 Alberto Morón Hernández
"""

import pytest

from depositduck.settings import Settings


def test_valid_settings(valid_settings_data: dict):
    try:
        settings = Settings(**valid_settings_data)
    except Exception as e:
        pytest.fail(str(e))

    assert settings.app_secret == valid_settings_data["app_secret"]
    assert settings.app_origin == valid_settings_data["app_origin"]


def test_default_values(clear_env_vars, valid_settings_data: dict):
    settings = Settings(**valid_settings_data)

    assert settings.app_name == "DepositDuck"
    assert settings.debug is False
    assert settings.db_port == 5432
    assert settings.smtp_port == 465
    assert settings.smtp_use_ssl is True
    assert settings.drallam_origin == "http://0.0.0.0:11434"
    assert settings.drallam_embeddings_model == "nomic-embed-text:v1.5"


def test_invalid_app_secret(valid_settings_data: dict):
    valid_settings_data["app_secret"] = "invalid_secret_key"

    with pytest.raises(ValueError) as exc_info:
        Settings(**valid_settings_data)

    assert "Fernet key must be 32 url-safe base64-encoded bytes" in str(exc_info.value)


def test_invalid_app_secret_type(valid_settings_data: dict):
    settings_data = valid_settings_data
    settings_data.update(
        {
            "app_secret": 12345,
        }
    )

    with pytest.raises(ValueError) as exc_info:
        Settings(**settings_data)

    assert "str" in str(exc_info.value)


def test_trailing_slash_removed(valid_settings_data: dict):
    app_origin = "https://example.com/"
    static_origin = "https://static.example.com/"
    settings_data = valid_settings_data

    settings_data.update(
        {
            "app_origin": app_origin,
            "static_origin": static_origin,
        }
    )
    settings = Settings(**valid_settings_data)

    assert settings.app_origin == app_origin[:-1]
    assert settings.static_origin == static_origin[:-1]
