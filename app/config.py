"""
Application configuration using environment variables.

Loads settings from .env file for author metadata and application settings.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Author Information
    author_name: str = "Wallace Espindola"
    author_email: str = "wallace@example.com"
    author_title: str = "Sr. Software Engineer / Solution Architect"
    author_bio: str = "Full-stack developer specializing in Python, Java, and JavaScript"

    # Social/Professional Links
    author_github: str = "https://github.com/wallaceespindola"
    author_linkedin: str = "https://www.linkedin.com/in/wallaceespindola/"
    author_speakerdeck: str = "https://speakerdeck.com/wallacese"

    # Application Settings
    app_title: str = "Schemas Demo: JSON vs Protobuf vs Avro"
    app_version: str = "0.1.0"
    app_description: str = "Practical comparison of three popular data serialization formats"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Using lru_cache ensures we only load .env once and reuse the same instance.
    """
    return Settings()
