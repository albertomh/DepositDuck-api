"""
(c) 2024 Alberto Morón Hernández
"""

from functools import lru_cache

from depositduck import config


@lru_cache
def get_settings():
    return config.Settings()
