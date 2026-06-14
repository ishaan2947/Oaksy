"""Application settings, loaded from environment / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database — SQLite by default so the app runs with zero external setup.
    database_url: str = "sqlite:///./oaksy.db"

    # Auth
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7  # one week
    jwt_algorithm: str = "HS256"

    # Claude AI verdict layer. Optional — empty key => graceful fallback.
    anthropic_api_key: str = ""
    ai_model: str = "claude-sonnet-4-6"

    # CORS — comma-separated origins.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
