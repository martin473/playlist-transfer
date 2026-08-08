"""Tests for Spotify authentication settings and loading."""

import os
from unittest.mock import patch

import pytest

from playlist_bridge.settings import (
    SpotifyOAuthSettings,
    load_spotify_settings_from_environment,
)


class TestSpotifyOAuthSettings:
    """Tests for SpotifyOAuthSettings model."""

    def test_create_with_valid_values(self) -> None:
        """Test creating SpotifyOAuthSettings with valid values."""
        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        assert settings.client_id == "test-client-id"
        assert settings.redirect_uri == "http://localhost:8080/callback"
        assert settings.scopes is not None
        assert len(settings.scopes) > 0

    def test_create_with_empty_client_id_raises_error(self) -> None:
        """Test that empty client_id raises ValueError."""
        with pytest.raises(ValueError, match="Spotify client_id must not be empty"):
            SpotifyOAuthSettings(
                client_id="",
                redirect_uri="http://localhost:8080/callback",
            )

    def test_create_with_empty_redirect_uri_raises_error(self) -> None:
        """Test that empty redirect_uri raises ValueError."""
        with pytest.raises(ValueError, match="Spotify redirect_uri must not be empty"):
            SpotifyOAuthSettings(
                client_id="test-client-id",
                redirect_uri="",
            )

    def test_create_with_whitespace_only_fields_raises_error(self) -> None:
        """Test that whitespace-only fields raise ValueError."""
        with pytest.raises(ValueError, match="Spotify client_id must not be empty"):
            SpotifyOAuthSettings(
                client_id="   ",
                redirect_uri="http://localhost:8080/callback",
            )


class TestLoadSpotifySettingsFromEnvironment:
    """Tests for load_spotify_settings_from_environment function."""

    def test_load_from_environment_all_variables_set(self) -> None:
        """Test loading with all environment variables set."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback",
                "SPOTIFY_SCOPES": "playlist-read-private user-read-email",
            },
        ):
            result = load_spotify_settings_from_environment()
            assert result.client_id == "test-client-id"
            assert result.redirect_uri == "http://localhost:8080/callback"
            assert result.scopes == ("playlist-read-private", "user-read-email")

    def test_load_with_default_scopes(self) -> None:
        """Test loading with only required environment variables."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback",
            },
        ):
            result = load_spotify_settings_from_environment()
            assert result.client_id == "test-client-id"
            assert result.redirect_uri == "http://localhost:8080/callback"
            # Should use default scopes from model
            assert result.scopes is not None
            assert len(result.scopes) > 0
            # Verify default scopes include expected values
            assert "playlist-read-private" in result.scopes
            assert "playlist-modify-public" in result.scopes

    def test_missing_client_id_raises_error(self) -> None:
        """Test that missing client ID raises ValueError."""
        with patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback"}):
            with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID"):
                load_spotify_settings_from_environment()

    def test_missing_redirect_uri_raises_error(self) -> None:
        """Test that missing redirect URI raises ValueError."""
        with patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "test-client-id"}):
            with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI"):
                load_spotify_settings_from_environment()

    def test_empty_client_id_raises_error(self) -> None:
        """Test that empty client ID raises ValueError."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "",
                "SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback",
            },
        ):
            with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID"):
                load_spotify_settings_from_environment()

    def test_empty_redirect_uri_raises_error(self) -> None:
        """Test that empty redirect URI raises ValueError."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_REDIRECT_URI": "",
            },
        ):
            with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI"):
                load_spotify_settings_from_environment()
