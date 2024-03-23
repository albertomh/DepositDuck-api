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

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

from depositduck.models.llm import AvailableLLM, LLMBase


class LLMChoice(LLMBase):
    model_config = ConfigDict(frozen=True)


class LLMSettings(BaseModel):
    embedding_model_name: str
    # not in dotenv, computed from `embedding_model_name` which _is_ in dotenv
    embedding_model: LLMChoice | None = None

    @model_validator(mode="after")
    def embedding_model_from_name(self) -> "LLMSettings":
        # toggle model_config's 'frozen' attribute to enable setting the derived field.
        model_choice = getattr(self, "embedding_model_name")
        self.model_config["frozen"] = False
        try:
            llm_choice = AvailableLLM[model_choice].value
            self.embedding_model = LLMChoice(**llm_choice.model_dump())
        except KeyError:
            raise ValueError(
                f"invalid model choice '{model_choice}' - "
                "check LLM__EMBEDDING_MODEL_NAME in .env "
            )
        self.model_config["frozen"] = True
        return self

    # 'frozen' must be True here or pydantic will not know to generate hash function for
    # this class, meaning it couldn't be used in a dependable decorated with @lru_cache.
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
