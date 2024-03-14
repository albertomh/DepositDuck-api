"""
(c) 2024 Alberto Morón Hernández
"""

import os
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


def is_running_under_pytest() -> bool:
    return os.environ.get("IS_TEST") is not None


class Settings(BaseSettings):
    app_name: str = "DepositDuck"
    debug: bool = False
    log_level: str = "warn"

    env_file: ClassVar = ".env.test" if is_running_under_pytest() else ".env"
    model_config = SettingsConfigDict(env_file=env_file)
