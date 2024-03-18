"""
(c) 2024 Alberto Morón Hernández
"""

import logging
from functools import lru_cache
from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape
from jinja2_fragments.fastapi import Jinja2Blocks
from structlog import configure, make_filtering_bound_logger
from structlog import get_logger as get_structlogger

from depositduck.settings import Settings

BASE_DIR = Path(__file__).resolve().parent


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
def get_settings():
    return Settings()


@lru_cache
def get_templates() -> Jinja2Templates:
    templates_dir_path = BASE_DIR / "web" / "templates"

    return Jinja2Blocks(
        directory=str(templates_dir_path),
        autoescape=select_autoescape(("html", "jinja2")),
    )
