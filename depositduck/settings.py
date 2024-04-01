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

from functools import cached_property

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from depositduck.models.llm import AvailableLLM


class LLMSettings(BaseModel):
    embedding_model_name: str

    # not in dotenv, computed from `embedding_model_name` which _is_ in dotenv
    @cached_property
    def embedding_model(self) -> AvailableLLM:
        model_name = self.embedding_model_name
        for llm in AvailableLLM:
            if llm.value.name == model_name:
                return llm
        raise ValueError(
            f"no AvailableLLM found matching 'embedding_model_name={model_name}'"
        )

    @model_validator(mode="after")
    def check_embedding_model(self: "LLMSettings") -> "LLMSettings":
        try:
            self.embedding_model
            return self
        except ValueError:
            raise

    model_config = ConfigDict(frozen=True)


class Settings(BaseSettings):
    app_name: str = "DepositDuck"
    # controls FastAPI's debug mode and whether or not to show `/docs`.
    debug: bool = False

    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int = 5432

    llm: LLMSettings

    model_config = SettingsConfigDict(env_nested_delimiter="__", frozen=True)
