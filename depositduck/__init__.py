"""
(c) 2024 Alberto Morón Hernández
"""

from pathlib import Path

# the FastAPI base directory, the dir this init file lives in
BASE_DIR = Path(__file__).resolve().parent

VERSION_MAJOR = 0
VERSION_MINOR = 6
VERSION_PATCH = 0

APIAPP_ROUTE_TAGS = [
    {"name": "healthcheck", "description": "Sub-system healthchecks"},
]

WEBAPP_ROUTE_TAGS = [
    {"name": "frontend", "description": "HTMX frontend"},
    {"name": "auth", "description": "Authentication operations"},
    {"name": "dashboard", "description": "Dashboard & onboarding"},
    {"name": "kitchensink", "description": "Development WIP"},
]
