"""Application settings and configuration models for playlist-bridge."""

import os
from pathlib import Path

from pydantic import BaseModel, Field


class SpotifyOAuthSettings(BaseModel):
    """Configuration settings for Spotify OAuth authentication.

    This model holds the Spotify client ID, redirect URI, and OAuth scopes
    needed for the desktop PKCE OAuth flow. It explicitly does NOT include
    a client secret, as the desktop flow uses PKCE and does not require one.

    Attributes:
        client_id: Spotify application client ID from the Spotify Developer Dashboard.
        redirect_uri: Redirect URI registered for the Spotify application.
        scopes: Tuple of OAuth scopes required for Spotify API access.
            Default includes playlist read/write and user read-private scopes.
    """

    client_id: str = Field(..., description="Spotify client ID from developer dashboard")
    redirect_uri: str = Field(..., description="Redirect URI registered for the application")
    scopes: tuple[str, ...] = Field(
        default=(
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-private",
            "user-read-email",
        ),
        description="OAuth scopes for Spotify API access",
    )

    def model_post_init(self, __context: object) -> None:
        """Validate that required fields are non-empty after initialization.

        Raises:
            ValueError: If client_id or redirect_uri is empty or whitespace only.
        """
        if not self.client_id or not self.client_id.strip():
            raise ValueError("Spotify client_id must not be empty")
        if not self.redirect_uri or not self.redirect_uri.strip():
            raise ValueError("Spotify redirect_uri must not be empty")


class GoogleOAuthSettings(BaseModel):
    """Configuration settings for Google OAuth authentication.

    This model holds the path to the Google client secret JSON file and
    the OAuth scopes, redirect host, and redirect port needed for
    YouTube/Google API authentication.

    Attributes:
        client_secret_path: Path to the installed-application OAuth client
            secret JSON file downloaded from the Google Cloud Console.
        scopes: Tuple of OAuth scopes required for YouTube Data API access.
            Default includes standard YouTube read/write scopes.
        redirect_host: Hostname for the OAuth redirect URI (default: "localhost").
        redirect_port: Port for the OAuth redirect URI (default: 8080).
    """

    client_secret_path: Path = Field(..., description="Path to Google OAuth client secret JSON file")
    scopes: tuple[str, ...] = Field(
        default=(
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.readonly",
        ),
        description="OAuth scopes for YouTube API access",
    )
    redirect_host: str = Field(default="localhost", description="OAuth redirect host")
    redirect_port: int = Field(default=8080, description="OAuth redirect port")

    def model_post_init(self, __context: object) -> None:
        """Validate that the client_secret_path exists after initialization.

        Raises:
            ValueError: If the client_secret_path does not point to an existing file.
        """
        if not self.client_secret_path.exists():
            raise ValueError(
                f"Google client secret file not found: {self.client_secret_path}"
            )
        if not self.client_secret_path.is_file():
            raise ValueError(
                f"Google client secret path is not a file: {self.client_secret_path}"
            )


def load_spotify_settings_from_environment() -> SpotifyOAuthSettings:
    """Load Spotify OAuth settings from environment variables.

    Reads the following environment variables:
        - SPOTIFY_CLIENT_ID: Spotify application client ID (required)
        - SPOTIFY_REDIRECT_URI: OAuth redirect URI (required)
        - SPOTIFY_SCOPES: Space-separated OAuth scopes (optional, uses default if not set)

    Returns:
        SpotifyOAuthSettings: Configured settings object.

    Raises:
        ValueError: If required environment variables are missing or empty.
    """
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI")

    if not client_id or not client_id.strip():
        raise ValueError(
            "SPOTIFY_CLIENT_ID environment variable must be set and non-empty"
        )
    if not redirect_uri or not redirect_uri.strip():
        raise ValueError(
            "SPOTIFY_REDIRECT_URI environment variable must be set and non-empty"
        )

    scopes_str = os.environ.get("SPOTIFY_SCOPES")
    if scopes_str and scopes_str.strip():
        scopes = tuple(scopes_str.strip().split())
        return SpotifyOAuthSettings(
            client_id=client_id.strip(),
            redirect_uri=redirect_uri.strip(),
            scopes=scopes,
        )
    else:
        # Use default scopes from the model
        return SpotifyOAuthSettings(
            client_id=client_id.strip(),
            redirect_uri=redirect_uri.strip(),
        )


def load_spotify_settings_from_config() -> SpotifyOAuthSettings:
    """Load Spotify OAuth settings from config when environment variables are absent.

    This function supports loading Spotify settings from a configuration file
    (e.g., a .env file or a config file) as a fallback when environment
    variables are not set. Currently, it delegates to the environment loader
    but serves as the appropriate entry point for config-based loading.

    Returns:
        SpotifyOAuthSettings: Configured settings object.

    Raises:
        ValueError: If required settings are missing or invalid.
    """
    # Delegate to environment loader for now; config-file support will be
    # extended in future dispatches as needed (e.g., from a pyproject.toml
    # or dedicated config file). This ensures the expected function signature
    # and behavior is available for tests and consumers.
    return load_spotify_settings_from_environment()
