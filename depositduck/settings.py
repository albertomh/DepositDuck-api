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

from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    model_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbeddingModel(BaseModel):
    # `name` is a tag from the ollama model library: https://ollama.com/library
    name: str = Field(frozen=True)
    dimensions: PositiveInt = Field(frozen=True)

    model_config = ConfigDict(frozen=True)


class EmbeddingModelChoice(Enum):
    # https://www.sbert.net/docs/pretrained_models.html
    MINILM_L6_V2 = EmbeddingModel(name="all-minilm:l6-v2", dimensions=384)


class LLMSettings(BaseModel):
    embedding_model_name: str
    # not in dotenv, computed from `embedding_model_name` which _is_ in dotenv
    embedding_model: EmbeddingModel | None = None

    @model_validator(mode="after")
    def embedding_model_from_name(self) -> "LLMSettings":
        # toggle model_config's 'frozen' attribute to enable setting the derived field.
        model_choice = getattr(self, "embedding_model_name")
        self.model_config["frozen"] = False
        try:
            self.embedding_model = EmbeddingModelChoice[model_choice].value
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
