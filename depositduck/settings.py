"""
Application configuration. Driven by environment variables.
Populate env vars by sourcing a .env file, which will be
picked up when the Settings object is instantiated.

Don't instantiate Settings directly from this module.
Use the `get_settings` dependable instead.

NB. `frozen=True` makes the Settings and nested objects hashable.
Making them hashable is needed so that dependables which require
a Settings object can be decorated with @lru_cache.

(c) 2024 Alberto Morón Hernández
"""

from pydantic import PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "DepositDuck"
    app_secret: str
    # controls FastAPI's debug mode and whether or not to show `/docs`.
    debug: bool = False

    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: PositiveInt = 5432

    smtp_server: str
    smtp_port: PositiveInt = 465  # for SSL
    smtp_sender_address: str
    smtp_password: str

    drallam_protocol: str = "http"
    drallam_host: str = "0.0.0.0"  # nosec B104
    drallam_port: PositiveInt = 11434
    drallam_embeddings_model: str = "nomic-embed-text:v1.5"

    model_config = SettingsConfigDict(env_nested_delimiter="__", frozen=True)
