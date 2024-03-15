"""
(c) 2024 Alberto Morón Hernández
"""

from functools import lru_cache
from pathlib import Path

from fastapi.templating import Jinja2Templates

from depositduck import config

BASE_DIR = Path(__file__).resolve().parent


@lru_cache
def get_settings():
    return config.Settings()


@lru_cache
def get_templates():
    templates_dir_path = BASE_DIR / "web" / "templates"
    return Jinja2Templates(directory=str(templates_dir_path))
