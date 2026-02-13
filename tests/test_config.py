"""Tests for configuration module."""

import pytest

from app.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Test settings have correct default values."""
    settings = Settings()

    assert settings.author_name == "Wallace Espindola"
    assert settings.author_email == "wallace@example.com"
    assert settings.author_title == "Sr. Software Engineer / Solution Architect"
    assert settings.app_title == "Schemas Demo: JSON vs Protobuf vs Avro"
    assert settings.app_version == "0.1.0"


def test_settings_github_link() -> None:
    """Test GitHub link format."""
    settings = Settings()
    assert "github.com" in settings.author_github
    assert settings.author_github.startswith("https://")


def test_settings_linkedin_link() -> None:
    """Test LinkedIn link format."""
    settings = Settings()
    assert "linkedin.com" in settings.author_linkedin
    assert settings.author_linkedin.startswith("https://")


def test_settings_speakerdeck_link() -> None:
    """Test Speaker Deck link format."""
    settings = Settings()
    assert "speakerdeck.com" in settings.author_speakerdeck
    assert settings.author_speakerdeck.startswith("https://")


def test_get_settings_cached() -> None:
    """Test that get_settings returns cached instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    # Should be the same object due to lru_cache
    assert settings1 is settings2


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test settings can be overridden by environment variables."""
    monkeypatch.setenv("AUTHOR_NAME", "Test Author")
    monkeypatch.setenv("AUTHOR_EMAIL", "test@example.com")
    monkeypatch.setenv("APP_VERSION", "1.0.0")

    # Clear the cache to force reload
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.author_name == "Test Author"
    assert settings.author_email == "test@example.com"
    assert settings.app_version == "1.0.0"

    # Restore cache
    get_settings.cache_clear()


def test_settings_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that environment variables are case insensitive."""
    monkeypatch.setenv("AUTHOR_NAME", "Lower Case")
    monkeypatch.setenv("author_email", "lower@example.com")

    get_settings.cache_clear()

    settings = get_settings()
    assert settings.author_name == "Lower Case"
    assert settings.author_email == "lower@example.com"

    get_settings.cache_clear()
