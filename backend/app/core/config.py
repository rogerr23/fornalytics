"""Application settings. This is the only module that reads environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file lives at the repository root, shared by backend and tooling.
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        # "KEY=" in .env means "not set": fall back to the default.
        env_ignore_empty=True,
    )

    # LLM
    llm_provider: Literal["gemini", "ollama"] = "gemini"
    gemini_api_key: str = ""
    gemini_model: str = ""
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""

    # Database
    database_url: str = ""
    database_url_direct: str = ""
    test_database_url: str = ""

    # Context limits
    max_context_tokens: int = 500_000
    chat_max_files: int = 8
    chat_context_tokens: int = 30_000

    # Upload limits
    max_upload_mb: int = 20
    max_unzipped_mb: int = 100
    max_files: int = 2000

    # Server
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
