"""
Application Configuration

Pydantic Settings for environment variable management.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Required:
        - DEEPGRAM_API_KEY: Deepgram API key for STT/TTS
        - GEMINI_API_KEY: Google Gemini API key for LLM
        - DAILY_API_KEY: Daily.co API key for WebRTC

    Optional:
        - DEBUG: Enable debug mode
        - LOG_LEVEL: Logging level
        - CORS_ORIGINS: Allowed CORS origins
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Required API keys
    deepgram_api_key: str
    google_api_key: str  # Gemini API key
    daily_api_key: str = ""  # Optional for MVP (chat-only mode)

    # Optional settings
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
