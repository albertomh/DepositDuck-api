"""
Callables to use with FastAPI's Dependency Injection system.
Expose functionality and data common across various routes,
eg. database sessions or application configuration.

(c) 2024 Alberto Morón Hernández
"""

import logging
from functools import cache
from typing import Annotated, AsyncGenerator, TypeVar

import httpx
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape
from jinja2_fragments.fastapi import Jinja2Blocks
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from structlog import configure, make_filtering_bound_logger
from structlog import get_logger as get_structlogger

from depositduck import BASE_DIR
from depositduck.settings import Settings

T = TypeVar("T")
AYieldFixture = AsyncGenerator[T, None]


@cache
def get_logger():
    """
    Usage:
      from structlog._config import BoundLoggerLazyProxy
      ...
      route(LOG: Annotated[BoundLoggerLazyProxy, Depends(get_logger)]):
          LOG.info("")
    """
    settings = get_settings()
    log_level = logging.DEBUG if settings.debug else logging.WARNING
    configure(wrapper_class=make_filtering_bound_logger(log_level))

    return get_structlogger()


@cache
def get_settings() -> Settings:
    return Settings()


@cache
def get_templates() -> Jinja2Templates:
    templates_dir_path = BASE_DIR / "web" / "templates"

    return Jinja2Blocks(
        directory=str(templates_dir_path),
        autoescape=select_autoescape(("html", "jinja2")),
    )


def get_db_connection_string(settings=None) -> str:
    if not settings:
        settings = get_settings()
    user = settings.db_user
    password = settings.db_password
    name = settings.db_name
    host = settings.db_host
    port = settings.db_port
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


@cache
def get_db_engine(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncEngine:
    return create_async_engine(get_db_connection_string(), echo=settings.debug)


async def get_db_session(
    engine: Annotated[AsyncEngine, Depends(get_db_engine)],
) -> AYieldFixture[AsyncSession]:
    # `expire_on_commit=False` allows accessing object attributes
    # even after a call to `AsyncSession.commit()`.
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# @cache
async def get_drallam_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AYieldFixture[httpx.AsyncClient]:
    drallam_url = (
        f"{settings.drallam_protocol}://{settings.drallam_host}:{settings.drallam_port}"
    )
    # create a new client for each request and close it once it is done
    async with httpx.AsyncClient(base_url=drallam_url) as client:
        yield client
