import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = (
        "postgresql+asyncpg://postgres:password@localhost:5432/berhan_pipeline"
    )
    database_url_sync: str = (
        "postgresql://postgres:password@localhost:5432/berhan_pipeline"
    )
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    url = os.getenv("DATABASE_URL")
    settings = Settings()
    if url:
        sync_url = url.replace("postgresql+asyncpg://", "postgresql://").replace(
            "postgresql://", "postgresql://"
        )
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            settings.database_url_sync = url
            settings.database_url = url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        elif "+asyncpg" in url:
            settings.database_url = url
            settings.database_url_sync = url.replace("+asyncpg", "", 1)
    return settings
