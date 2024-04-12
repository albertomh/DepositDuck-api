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
from fastapi import Depends, HTTPException, Request, status
from jinja2 import select_autoescape
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from starlette.responses import Response
from structlog import configure, make_filtering_bound_logger
from structlog import get_logger as get_structlogger

from depositduck import BASE_DIR
from depositduck.models.sql.auth import User
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


class AuthenticatedJinjaBlocks(Jinja2Blocks):
    """
    Derived class to ensure the TemplateResponse context has a request and a user passed
    to it. Even if the user is None to denote an unauthenticated request.
    """

    class TemplateContext(BaseModel):
        request: Request
        user: User | None

        model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def TemplateResponse(
        self, name: str, context: TemplateContext, *args, **kwargs
    ) -> Response:
        if not isinstance(context, self.TemplateContext):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "jinja block TemplateResponse received context not conforming to "
                    "TemplateContext"
                ),
            )

        return super().TemplateResponse(name, context.model_dump(), *args, **kwargs)


@cache
def get_templates() -> AuthenticatedJinjaBlocks:
    templates_dir_path = BASE_DIR / "web" / "templates"

    return AuthenticatedJinjaBlocks(
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


db_engine = create_async_engine(get_db_connection_string(), echo=get_settings().debug)

# `expire_on_commit=False` allows accessing object attributes
# even after a call to `AsyncSession.commit()`.
db_session = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
