"""Service configuration via environment variables (12-factor)."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HEALTH_", env_file=".env")

    service_name: str = "health-service"
    version: str = "0.1.0"
    environment: str = "local"


settings = Settings()
