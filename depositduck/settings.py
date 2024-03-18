"""
Application configuration. Driven by environment variables.
Populate env vars by sourcing a .env file, which will be
picked up when the Settings object is instantiated.

Don't instantiate Settings directly from this module.
Use the `get_settings` dependable instead.

(c) 2024 Alberto Morón Hernández
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DepositDuck"
    # controls FastAPI's debug mode and whether or not to show `/docs`.
    debug: bool = False

    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int = 5432

    # `frozen=True` is needed to make object hashable. Making it hashable is needed so
    # that dependables which require a Settings objects can have a lru_cache.
    model_config = SettingsConfigDict(frozen=True)
