"""
(c) 2024 Alberto Morón Hernández
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def is_running_under_pytest() -> bool:
    return "PYTEST_CURRENT_TEST" in os.environ


class Settings(BaseSettings):
    app_name: str = "DepositDuck"
    debug: bool = False
    log_level: str = "warn"

    model_config = SettingsConfigDict(env_file=".env")
