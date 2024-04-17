"""
(c) 2024 Alberto Morón Hernández
"""

import logging
import os
from typing import Any

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

VALID_FERNET_KEY = "ie6_e7cxZjIs_SAXsZzYLARaQTnhF16DYTCUUTdKgTQ="


def get_valid_settings_data() -> dict[str, Any]:
    return {
        "app_secret": VALID_FERNET_KEY,
        "app_origin": "http://www.depositduck-test.tld",
        "db_user": "db_user",
        "db_password": "db_password",
        "db_name": "db_name",
        "db_host": "localhost",
        "smtp_server": "smtp.sendservice.mail",
        "smtp_sender_address": "sender@depositduck-test.tld",
        "smtp_password": "smtp_password",
        "static_origin": "https://bucket.provider.cloud",
        "speculum_release": "1.0.0",
    }


@pytest_asyncio.fixture(scope="session", autouse=True)
def LOG():
    return logging.getLogger(__name__)


@pytest.fixture()
def clear_env_vars():
    original_env = dict(os.environ)
    os.environ.clear()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest_asyncio.fixture
async def web_client():
    from depositduck.main import webapp

    web_client = await get_aclient(webapp, "http://webtest")
    async with web_client as client:
        yield client


@pytest_asyncio.fixture
async def api_client():
    from depositduck.main import apiapp

    api_client = await get_aclient(apiapp, "http://apitest")
    async with api_client as client:
        yield client


@pytest_asyncio.fixture
async def llm_client():
    from depositduck.main import llmapp

    llm_client = await get_aclient(llmapp, "http://llmtest")
    async with llm_client as client:
        yield client


@pytest.fixture
def valid_settings_data() -> dict[str, Any]:
    return {
        "app_secret": VALID_FERNET_KEY,
        "app_origin": "http://www.depositduck-test.tld",
        "db_user": "db_user",
        "db_password": "db_password",
        "db_name": "db_name",
        "db_host": "localhost",
        "smtp_server": "smtp.sendservice.mail",
        "smtp_sender_address": "sender@depositduck-test.tld",
        "smtp_password": "smtp_password",
        "static_origin": "https://bucket.provider.cloud",
        "speculum_release": "1.0.0",
    }
