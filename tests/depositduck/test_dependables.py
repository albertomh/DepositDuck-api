"""
(c) 2024 Alberto Morón Hernández
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from depositduck.dependables import get_db_engine, get_settings


@pytest.mark.skip(reason="TODO: stub")
def test_get_templates():
    pass


def test_get_db_engine(monkeypatch):
    patched_settings = {
        "db_user": "db_engine_test_user",
        "db_password": "db_engine_test_password",
        "db_name": "db_engine_test_name",
    }
    settings = get_settings()
    for key, value in patched_settings.items():
        monkeypatch.setitem(settings.__dict__, key, value)
    engine = get_db_engine(settings)

    assert isinstance(engine, AsyncEngine)
    assert engine.url.username == patched_settings["db_user"]
    assert engine.url.password == patched_settings["db_password"]
    assert engine.url.database == patched_settings["db_name"]
    assert engine.url.port == 5432
