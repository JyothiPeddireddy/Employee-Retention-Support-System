"""Application settings, loaded from environment / .env (never hard-code secrets)."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Default to local SQLite database so it works out-of-the-box anywhere;
    # Can be overridden via DATABASE_URL=postgresql+psycopg://...
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./retention.db")
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    generator_seed: int = 20261022
    default_scale: int = 10000
    cors_origins: str = "*"


@lru_cache
def get_settings() -> Settings:
    return Settings()
