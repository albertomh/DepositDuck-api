"""
(c) 2024 Alberto Morón Hernández
"""

import logging
import os
from typing import Callable
from unittest.mock import AsyncMock, Mock
import uuid

import pytest
import pytest_asyncio
from fastapi import FastAPI, Request
from fastapi_users.authentication.strategy.db import DatabaseStrategy
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from depositduck.auth.dependables import UserManager
from depositduck.dependables import AuthenticatedJinjaBlocks, get_settings
from depositduck.main import get_apiapp, get_llmapp, get_webapp
from depositduck.models.sql.auth import User
from depositduck.settings import Settings

VALID_FERNET_KEY = "ie6_e7cxZjIs_SAXsZzYLARaQTnhF16DYTCUUTdKgTQ="

# TODO: add Faker


def get_valid_settings() -> Settings:
    return Settings(
        app_secret=VALID_FERNET_KEY,
        app_origin="http://www.depositduck-test.tld",
        db_user="db_user",
        db_password="db_password",
        db_name="db_name",
        db_host="localhost",
        smtp_server="smtp.sendservice.mail",
        smtp_sender_address="sender@depositduck-test.tld",
        smtp_password="smtp_password",
        static_origin="https://bucket.provider.cloud",
        speculum_release="1.5.0",
    )


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


async def _create_client_factory(
    app_getter: Callable[[Settings], FastAPI],
    base_url: str,
    settings: Settings | None = None,
    dependency_overrides: dict[Callable, Callable] | None = None,
) -> AsyncClient:
    """
    Usage:
      Use any of the public fixtures that wrap this function: `web_client_factory`,
      `api_client_factory` and `llm_client_factory`.

      ```python
      @pytest.mark.asyncio
      async def test_example(web_client_factory):
            settings = Settings(**{...})
            web_client = await web_client_factory(
                settings=settings, dependency_overrides=None
            )
            async with web_client as client:
                response = await client.get("/path")
      ```
    """
    if not settings:
        settings = get_settings()
    app: FastAPI = app_getter(settings)
    if dependency_overrides:
        for dependency, override in dependency_overrides.items():
            app.dependency_overrides[dependency] = override
    # TODO: refactor to use `from fastapi.testclient import TestClient` instead
    client = AsyncClient(transport=ASGITransport(app=app), base_url=base_url)  # type: ignore
    return client


@pytest.fixture
def web_client_factory():
    async def _create_web_client(
        *,
        settings: Settings | None = None,
        dependency_overrides: dict[Callable, Callable] | None = None,
    ):
        return await _create_client_factory(
            get_webapp, "http://webtest", settings, dependency_overrides
        )

    return _create_web_client


@pytest.fixture
def api_client_factory():
    async def _create_api_client(
        *,
        settings: Settings | None = None,
        dependency_overrides: dict[Callable, Callable] | None = None,
    ):
        return await _create_client_factory(
            get_apiapp, "http://apitest", settings, dependency_overrides
        )

    return _create_api_client


@pytest.fixture
def llm_client_factory():
    async def _create_llm_client(
        *,
        settings: Settings | None = None,
        dependency_overrides: dict[callable, callable] | None = None,
    ):
        return await _create_client_factory(
            get_llmapp, "http://llmtest", settings, dependency_overrides
        )

    return _create_llm_client


class AsyncContextManagerMock(Mock):
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        pass


@pytest.fixture
def mock_async_session():
    """
    Replaces the object returned by `db_session.begin()`. Where `db_session` is the
    mocked `db_session_factory` dependable.
    """
    mock_session = AsyncMock()
    mock_session.return_value.__aenter__.return_value = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def mock_async_sessionmaker(mock_async_session):
    """Replaces the `db_session_factory` dependable."""
    mock_sessionmaker = Mock(spec=async_sessionmaker)
    mock_sessionmaker.begin = AsyncContextManagerMock(return_value=mock_async_session)
    mock_sessionmaker.begin.return_value.__aenter__.return_value = mock_async_session
    return mock_sessionmaker


@pytest.fixture
def mock_request():
    return Mock(spec=Request)


@pytest.fixture
def mock_user():
    mock_user = Mock(spec=User)
    mock_user.id = uuid.uuid4()
    return mock_user


@pytest.fixture
def mock_auth_db_strategy():
    return Mock(spec=DatabaseStrategy)


@pytest.fixture
def mock_user_manager(mock_user):
    mock_manager = AsyncMock(spec=UserManager)
    mock_manager.create = AsyncMock(return_value=mock_user)
    return mock_manager


@pytest.fixture
def mock_settings():
    mock_settings = Mock(spec=Settings)
    mock_settings.app_name = "DepositDuck-Test"
    mock_settings.debug = False
    mock_settings.e2e = False
    return mock_settings


@pytest.fixture
def mock_authenticated_jinja_blocks():
    return Mock(spec=AuthenticatedJinjaBlocks)
