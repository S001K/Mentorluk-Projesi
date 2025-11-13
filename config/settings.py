# config/settings.py
from __future__ import annotations

from enum import Enum
from functools import lru_cache
from typing import Optional, Dict

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported large language model backends."""
    GROQ = "groq"
    OPENROUTER = "openrouter"


class Settings(BaseSettings):
    """
    Centralized configuration for the application.
    All values come from `.env`.
    Persona prompts remain static in code by default.
    """

    # --- LLM Configuration ---
    LLM_PROVIDER: LLMProvider
    LLM_MODEL: str

    # --- Provider API Keys (conditional) ---
    OPENROUTER_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # --- Redis (short-term memory) ---
    REDIS_URL: str
    DEFAULT_SESSION_ID: str
    MEMORY_WINDOW_SIZE: int
    REDIS_TTL_SECONDS: int = 1800  # default: 30 minutes

    # --- Logging ---
    LOG_LEVEL: str = "INFO"

    # --- Static persona system ---
    PERSONA_PROMPTS: Dict[str, str] = {
        "miki": "conversation_agent_miki_system_prompt.j2",
        "alex": "conversation_agent_alex_system_prompt.j2",
        "kaito": "conversation_agent_kaito_system_prompt.j2",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def _require_provider_key(self) -> "Settings":
        """Ensure the correct API key is present for the selected provider."""
        if self.LLM_PROVIDER is LLMProvider.OPENROUTER and not self.OPENROUTER_API_KEY:
            raise ValueError(
                "OPENROUTER_API_KEY is required when LLM_PROVIDER='openrouter'."
            )
        if self.LLM_PROVIDER is LLMProvider.GROQ and not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required when LLM_PROVIDER='groq'."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Singleton factory for application settings."""
    return Settings()


# Import and use this everywhere
SETTINGS: Settings = get_settings()
