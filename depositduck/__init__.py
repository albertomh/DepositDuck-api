"""
(c) 2024 Alberto Morón Hernández
"""

from pathlib import Path

# the FastAPI base directory, the dir this init file lives in
BASE_DIR = Path(__file__).resolve().parent

VERSION_MAJOR = 0
VERSION_MINOR = 3
VERSION_PATCH = 0

ROUTE_TAGS_METADATA = [
    {"name": "frontend", "description": "HTMX frontend"},
    {"name": "auth", "description": "Authentication operations"},
    {"name": "ops", "description": "Internal ops - healthchecks, etc."},
    {"name": "kitchensink", "description": "Development WIP"},
]
