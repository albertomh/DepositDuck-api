"""
(c) 2024 Alberto Morón Hernández
"""

import pytest

from depositduck.settings import Settings
from tests.unit.conftest import get_valid_settings_data


def test_valid_settings():
    settings_data = get_valid_settings_data()
    try:
        settings = Settings(**settings_data)
    except Exception as e:
        pytest.fail(str(e))

    assert settings.app_secret == settings_data["app_secret"]
    assert settings.app_origin == settings_data["app_origin"]


def test_default_values(clear_env_vars):
    settings = Settings(**get_valid_settings_data())

    assert settings.app_name == "DepositDuck"
    assert settings.debug is False
    assert settings.db_port == 5432
    assert settings.smtp_port == 465
    assert settings.smtp_use_ssl is True
    assert settings.drallam_origin == "http://0.0.0.0:11434"
    assert settings.drallam_embeddings_model == "nomic-embed-text:v1.5"


def test_invalid_app_secret():
    settings_data = get_valid_settings_data()
    settings_data["app_secret"] = "invalid_secret_key"

    with pytest.raises(ValueError) as exc_info:
        Settings(**settings_data)

    assert "Fernet key must be 32 url-safe base64-encoded bytes" in str(exc_info.value)


def test_invalid_app_secret_type():
    settings_data = get_valid_settings_data()
    settings_data.update(
        {
            "app_secret": 12345,
        }
    )

    with pytest.raises(ValueError) as exc_info:
        Settings(**settings_data)

    assert "str" in str(exc_info.value)


def test_trailing_slash_removed():
    app_origin = "https://example.com/"
    static_origin = "https://static.example.com/"
    settings_data = get_valid_settings_data()

    settings_data.update(
        {
            "app_origin": app_origin,
            "static_origin": static_origin,
        }
    )
    settings = Settings(**settings_data)

    assert settings.app_origin == app_origin[:-1]
    assert settings.static_origin == static_origin[:-1]
