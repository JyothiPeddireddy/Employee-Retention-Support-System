"""Application settings loaded from environment or .env file."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    app_name: str = "Employee Retention Support System"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # PostgreSQL Connection String (configurable via .env)
    # Format: postgresql+psycopg://<username>:<password>@<host>:<port>/<dbname>
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/retention_db"
    )

    # Security & Auth
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-key-change-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Synthetic Data Parameters
    generator_seed: int = 20261022
    default_scale: int = 10000

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
