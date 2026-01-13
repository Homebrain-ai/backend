"""
app/settings.py
"""

from functools import cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App
    env: str = Field(default="dev")
    debug: bool = Field(default=False)

    # --- DB
    database_url: str
    langgraph_db_url: str | None = None

    # --- llm
    gemini_api_key: SecretStr
    gemini_model: str = Field(min_length=1)
    gemini_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    gemini_max_retries: int = Field(default=2, ge=0, le=10)

    # --- RAG
    rag_docs_dir: Path
    rag_vector_dir: Path

    # --- Router
    router_min_confidence: float = Field(default=0.55, ge=0.0, le=1.0)
    router_interrupt_on_ambiguity: bool = Field(default=True)

@cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
