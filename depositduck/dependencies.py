"""
(c) 2024 Alberto Morón Hernández
"""

from functools import lru_cache
from pathlib import Path

from fastapi.templating import Jinja2Templates
from jinja2 import select_autoescape
from jinja2_fragments.fastapi import Jinja2Blocks

from depositduck import config

BASE_DIR = Path(__file__).resolve().parent


@lru_cache
def get_settings():
    return config.Settings()


@lru_cache
def get_templates() -> Jinja2Templates:
    templates_dir_path = BASE_DIR / "web" / "templates"
    return Jinja2Blocks(
        directory=str(templates_dir_path),
        autoescape=select_autoescape(("html", "jinja2")),
    )
