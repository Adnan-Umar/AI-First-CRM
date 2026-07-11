from functools import lru_cache
import json
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "AI-First CRM API"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://crm_user:crm_pass@localhost:5432/ai_first_crm"
    DB_AUTO_CREATE: bool = False
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "gemma2-9b-it"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from a comma-separated string or a JSON array."""
        raw = (self.CORS_ORIGINS or "").strip()
        if raw.startswith("[") and raw.endswith("]"):
            try:
                return [str(item).strip() for item in json.loads(raw) if str(item).strip()]
            except json.JSONDecodeError:
                pass
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
