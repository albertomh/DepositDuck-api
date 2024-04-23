"""
Callables to use with FastAPI's Dependency Injection system.
Expose functionality and data common across various routes,
eg. database sessions or application configuration.

(c) 2024 Alberto Morón Hernández
"""

import logging
from functools import cache
from typing import Annotated, AsyncGenerator, ClassVar, TypeVar

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
from starlette.templating import _TemplateResponse
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
    Derived class to add objects needed by all responses to the TemplateResponse context.
    Namely, the request, the user and where to find static assets.
    The user may be None to denote an unauthenticated request.

    Usage:
      consult the `get_templates` dependable.
    """

    class TemplateContext(BaseModel):
        settings: ClassVar[Settings] = get_settings()
        speculum_source: str = f"{settings.static_origin}/{settings.speculum_release}"
        request: Request
        user: User | None
        # TODO: add other sensible defaults that I may want to set based on context
        #       eg. `show_footer_links` should default to True but may want to set
        #       to False to reduce distractions on eg. /signup/ page.

        model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def TemplateResponse(
        self, template_name: str, context: TemplateContext, *args, **kwargs
    ) -> _TemplateResponse:
        if not isinstance(context, self.TemplateContext):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "jinja block TemplateResponse received context not conforming to "
                    "TemplateContext"
                ),
            )

        return super().TemplateResponse(
            template_name, context.model_dump(), *args, **kwargs
        )


@cache
def get_templates() -> AuthenticatedJinjaBlocks:
    """
    Usage:
      @router.get("/path/")
      async def path_func(
        templates: Annotated[AuthenticatedJinjaBlocks, Depends(get_templates)],
        request: Request,
      ):
      ...
      context = AuthenticatedJinjaBlocks.TemplateContext(
          request=request,
          user=user,
          key=value,  # arbitrary kwargs will propagate to the template
      )
      return templates.TemplateResponse(
          "dir/template.html.jinja2", context=context, [block_name="fragment_id"]
      )
    """
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
    # create a new client for each request and close it once it is done
    async with httpx.AsyncClient(base_url=settings.drallam_origin) as client:
        yield client


db_engine = create_async_engine(get_db_connection_string(), echo=get_settings().debug)


async def db_session_factory() -> async_sessionmaker:
    """
    Usage:
    ```python
      async def example_route(
          db_session_factory: Annotated[async_sessionmaker, Depends(db_session_factory)],
      ) -> Response:
          session: AsyncSession
          async with db_session.begin() as session:
              ...
              session.add(model_instance)
    ```
    """
    # `expire_on_commit=False` allows accessing object attributes
    # even after a call to `AsyncSession.commit()`.
    return async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
