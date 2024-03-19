"""
Callables to use with FastAPI's Dependency Injection system.
Expose functionality and data common across various routes,
eg. database sessions or application configuration.

(c) 2024 Alberto Morón Hernández
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Annotated, AsyncGenerator, TypeVar

from fastapi import Depends
from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape
from jinja2_fragments.fastapi import Jinja2Blocks
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from structlog import configure, make_filtering_bound_logger
from structlog import get_logger as get_structlogger

from depositduck.settings import Settings

BASE_DIR = Path(__file__).resolve().parent

T = TypeVar("T")
AYieldFixture = AsyncGenerator[T, None]


@lru_cache
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


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_templates() -> Jinja2Templates:
    templates_dir_path = BASE_DIR / "web" / "templates"

    return Jinja2Blocks(
        directory=str(templates_dir_path),
        autoescape=select_autoescape(("html", "jinja2")),
    )


@lru_cache
def get_db_engine(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncEngine:
    user = settings.db_user
    password = settings.db_password
    name = settings.db_name
    host = settings.db_host
    port = settings.db_port
    connection_str = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"
    return create_async_engine(connection_str, echo=settings.debug)


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
