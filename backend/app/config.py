from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the palm reading API."""

    app_name: str = "Palm Reading API"
    data_dir: Path = Field(default=Path(__file__).resolve().parents[1] / "data")
    max_upload_bytes: int = 10 * 1024 * 1024
    retention_days: int = 7
    ai_analysis_enabled: bool = True
    ai_provider: str = "mock"
    ai_api_key: str | None = None
    ai_base_url: str = "https://api.openai.com/v1"
    ai_model: str = "gpt-4o-mini"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_prefix="PALM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
