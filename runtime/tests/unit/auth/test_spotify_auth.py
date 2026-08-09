"""Tests for Spotify authentication settings and manager."""

import os
from unittest.mock import MagicMock, patch

import pytest

from playlist_bridge.auth.spotify import create_spotify_pkce_manager
from playlist_bridge.credentials.store import KeyringCacheHandler
from playlist_bridge.settings import (
    SpotifyOAuthSettings,
    load_spotify_settings_from_environment,
    load_spotify_settings_from_config,
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


class TestLoadSpotifySettingsFromConfig:
    """Tests for load_spotify_settings_from_config function."""

    def test_load_from_environment_all_variables_set(self) -> None:
        """Test loading with all environment variables set via config loader."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback",
                "SPOTIFY_SCOPES": "playlist-read-private user-read-email",
            },
        ):
            result = load_spotify_settings_from_config()
            assert result.client_id == "test-client-id"
            assert result.redirect_uri == "http://localhost:8080/callback"
            assert result.scopes == ("playlist-read-private", "user-read-email")

    def test_load_with_default_scopes(self) -> None:
        """Test loading with only required environment variables via config loader."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback",
            },
        ):
            result = load_spotify_settings_from_config()
            assert result.client_id == "test-client-id"
            assert result.redirect_uri == "http://localhost:8080/callback"
            assert result.scopes is not None
            assert len(result.scopes) > 0
            assert "playlist-read-private" in result.scopes

    def test_missing_client_id_raises_error(self) -> None:
        """Test that missing client ID raises ValueError from config loader."""
        with patch.dict(os.environ, {"SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback"}):
            with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID"):
                load_spotify_settings_from_config()

    def test_missing_redirect_uri_raises_error(self) -> None:
        """Test that missing redirect URI raises ValueError from config loader."""
        with patch.dict(os.environ, {"SPOTIFY_CLIENT_ID": "test-client-id"}):
            with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI"):
                load_spotify_settings_from_config()

    def test_empty_client_id_raises_error(self) -> None:
        """Test that empty client ID raises ValueError from config loader."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "",
                "SPOTIFY_REDIRECT_URI": "http://localhost:8080/callback",
            },
        ):
            with pytest.raises(ValueError, match="SPOTIFY_CLIENT_ID"):
                load_spotify_settings_from_config()

    def test_empty_redirect_uri_raises_error(self) -> None:
        """Test that empty redirect URI raises ValueError from config loader."""
        with patch.dict(
            os.environ,
            {
                "SPOTIFY_CLIENT_ID": "test-client-id",
                "SPOTIFY_REDIRECT_URI": "",
            },
        ):
            with pytest.raises(ValueError, match="SPOTIFY_REDIRECT_URI"):
                load_spotify_settings_from_config()


class TestCreateSpotifyPkceManager:
    """Tests for create_spotify_pkce_manager function."""

    def test_create_manager_with_valid_args(self) -> None:
        """Test creating SpotifyPKCE manager with valid arguments."""
        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
            scopes=("playlist-read-private", "user-read-email"),
        )
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)

        with patch("playlist_bridge.auth.spotify.SpotifyPKCE") as mock_spotify_pkce:
            mock_instance = MagicMock()
            mock_spotify_pkce.return_value = mock_instance

            result = create_spotify_pkce_manager(
                settings=settings,
                cache_handler=mock_cache_handler,
                open_browser=False,
            )

            mock_spotify_pkce.assert_called_once_with(
                client_id="test-client-id",
                redirect_uri="http://localhost:8080/callback",
                scope=["playlist-read-private", "user-read-email"],
                cache_handler=mock_cache_handler,
                open_browser=False,
            )
            assert result == mock_instance

    def test_create_manager_with_default_open_browser(self) -> None:
        """Test that open_browser defaults to True."""
        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)

        with patch("playlist_bridge.auth.spotify.SpotifyPKCE") as mock_spotify_pkce:
            mock_instance = MagicMock()
            mock_spotify_pkce.return_value = mock_instance

            result = create_spotify_pkce_manager(
                settings=settings,
                cache_handler=mock_cache_handler,
            )

            mock_spotify_pkce.assert_called_once_with(
                client_id="test-client-id",
                redirect_uri="http://localhost:8080/callback",
                scope=list(settings.scopes),
                cache_handler=mock_cache_handler,
                open_browser=True,
            )
            assert result == mock_instance

    def test_create_manager_with_none_settings_raises_error(self) -> None:
        """Test that None settings raises ValueError."""
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)
        with pytest.raises(ValueError, match="settings must not be None"):
            create_spotify_pkce_manager(
                settings=None,  # type: ignore
                cache_handler=mock_cache_handler,
            )

    def test_create_manager_with_none_cache_handler_raises_error(self) -> None:
        """Test that None cache_handler raises ValueError."""
        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        with pytest.raises(ValueError, match="cache_handler must not be None"):
            create_spotify_pkce_manager(
                settings=settings,
                cache_handler=None,  # type: ignore
            )

    def test_create_manager_converts_scopes_tuple_to_list(self) -> None:
        """Test that scopes tuple is properly converted to a list."""
        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
            scopes=("scope1", "scope2", "scope3"),
        )
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)

        with patch("playlist_bridge.auth.spotify.SpotifyPKCE") as mock_spotify_pkce:
            mock_instance = MagicMock()
            mock_spotify_pkce.return_value = mock_instance

            create_spotify_pkce_manager(
                settings=settings,
                cache_handler=mock_cache_handler,
            )

            mock_spotify_pkce.assert_called_once_with(
                client_id="test-client-id",
                redirect_uri="http://localhost:8080/callback",
                scope=["scope1", "scope2", "scope3"],
                cache_handler=mock_cache_handler,
                open_browser=True,
            )



class TestAuthenticateSpotifyProfile:
    """Tests for authenticate_spotify_profile function."""

    def test_authenticate_spotify_profile_success(self) -> None:
        """Test successful Spotify authentication with callback handling."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile
        from playlist_bridge.domain.enums import DestinationService, SourceService
        from playlist_bridge.domain.models import AccountProfile

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
            scopes=("playlist-read-private", "user-read-email"),
        )
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)

        # Mock the token info returned by SpotifyPKCE
        mock_token_info = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600,
            "scope": "playlist-read-private user-read-email",
        }

        # Mock user info returned by Spotify API
        mock_user_info = {
            "id": "mock-user-id",
            "display_name": "Mock User",
            "email": "mock@example.com",
            "external_urls": {"spotify": "https://open.spotify.com/user/mock-user-id"},
        }

        # Mock the AccountProfile that will be saved
        mock_profile = AccountProfile(
            provider="spotify",
            account_id="mock-user-id",
            display_name="Mock User",
            email="mock@example.com",
            username="Mock User",
            profile_url="https://open.spotify.com/user/mock-user-id",
        )

        with patch(
            "playlist_bridge.auth.spotify.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler_class.return_value = mock_cache_handler

            with patch(
                "playlist_bridge.auth.spotify.create_spotify_pkce_manager"
            ) as mock_create_manager:
                mock_pkce = MagicMock()
                mock_pkce.get_access_token.return_value = mock_token_info
                mock_create_manager.return_value = mock_pkce

                with patch("spotipy.Spotify") as mock_spotify_class:
                    mock_spotify_client = MagicMock()
                    mock_spotify_client.me.return_value = mock_user_info
                    mock_spotify_class.return_value = mock_spotify_client

                    mock_profiles.save.return_value = mock_profile

                    result = authenticate_spotify_profile(
                        profile_name="test-profile",
                        settings=settings,
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                        open_browser=False,
                    )

                    # Verify the cache handler was created with credentials
                    mock_cache_handler_class.assert_called_once_with(mock_credentials)

                    # Verify the PKCE manager was created
                    mock_create_manager.assert_called_once_with(
                        settings=settings,
                        cache_handler=mock_cache_handler,
                        open_browser=False,
                    )

                    # Verify get_access_token was called
                    mock_pkce.get_access_token.assert_called_once_with(as_dict=True)

                    # Verify the Spotify client was created with the access token
                    mock_spotify_class.assert_called_once_with(
                        auth="mock-access-token"
                    )
                    mock_spotify_client.me.assert_called_once()

                    # Verify the profile was saved
                    mock_profiles.save.assert_called_once()
                    saved_profile_arg = mock_profiles.save.call_args[0][0]
                    assert saved_profile_arg.provider == "spotify"
                    assert saved_profile_arg.account_id == "mock-user-id"
                    assert saved_profile_arg.display_name == "Mock User"
                    assert saved_profile_arg.email == "mock@example.com"

                    # Verify the result is the saved profile
                    assert result == mock_profile

    def test_authenticate_spotify_profile_authentication_required(self) -> None:
        """Test that AuthenticationRequired is raised when auth fails."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile
        from playlist_bridge.providers.errors import AuthenticationRequired

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)

        with patch(
            "playlist_bridge.auth.spotify.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler_class.return_value = mock_cache_handler

            with patch(
                "playlist_bridge.auth.spotify.create_spotify_pkce_manager"
            ) as mock_create_manager:
                mock_pkce = MagicMock()
                # Simulate failed authentication (returns None)
                mock_pkce.get_access_token.return_value = None
                mock_create_manager.return_value = mock_pkce

                with pytest.raises(AuthenticationRequired) as exc_info:
                    authenticate_spotify_profile(
                        profile_name="test-profile",
                        settings=settings,
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                        open_browser=False,
                    )

                assert "Failed to obtain Spotify access token" in str(exc_info.value)

    def test_authenticate_spotify_profile_empty_profile_name(self) -> None:
        """Test that empty profile_name raises ValueError."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        with pytest.raises(ValueError, match="profile_name must not be empty"):
            authenticate_spotify_profile(
                profile_name="",
                settings=settings,
                profiles=mock_profiles,
                credentials=mock_credentials,
            )

        with pytest.raises(ValueError, match="profile_name must not be empty"):
            authenticate_spotify_profile(
                profile_name="   ",
                settings=settings,
                profiles=mock_profiles,
                credentials=mock_credentials,
            )

    def test_authenticate_spotify_profile_none_settings(self) -> None:
        """Test that None settings raises ValueError."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        with pytest.raises(ValueError, match="settings must not be None"):
            authenticate_spotify_profile(
                profile_name="test-profile",
                settings=None,  # type: ignore
                profiles=mock_profiles,
                credentials=mock_credentials,
            )

    def test_authenticate_spotify_profile_none_profiles(self) -> None:
        """Test that None profiles repository raises ValueError."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_credentials = MagicMock()

        with pytest.raises(ValueError, match="profiles repository must not be None"):
            authenticate_spotify_profile(
                profile_name="test-profile",
                settings=settings,
                profiles=None,  # type: ignore
                credentials=mock_credentials,
            )

    def test_authenticate_spotify_profile_none_credentials(self) -> None:
        """Test that None credentials store raises ValueError."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_profiles = MagicMock()

        with pytest.raises(ValueError, match="credentials store must not be None"):
            authenticate_spotify_profile(
                profile_name="test-profile",
                settings=settings,
                profiles=mock_profiles,
                credentials=None,  # type: ignore
            )

    def test_authenticate_spotify_profile_invalid_user_response(self) -> None:
        """Test that InvalidProviderResponse is raised when user response is malformed."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile
        from playlist_bridge.providers.errors import InvalidProviderResponse

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_cache_handler = MagicMock(spec=KeyringCacheHandler)

        mock_token_info = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600,
        }

        with patch(
            "playlist_bridge.auth.spotify.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler_class.return_value = mock_cache_handler

            with patch(
                "playlist_bridge.auth.spotify.create_spotify_pkce_manager"
            ) as mock_create_manager:
                mock_pkce = MagicMock()
                mock_pkce.get_access_token.return_value = mock_token_info
                mock_create_manager.return_value = mock_pkce

                with patch("spotipy.Spotify") as mock_spotify_class:
                    mock_spotify_client = MagicMock()
                    # User response missing the 'id' field
                    mock_spotify_client.me.return_value = {"display_name": "Mock User"}
                    mock_spotify_class.return_value = mock_spotify_client

                    with pytest.raises(InvalidProviderResponse) as exc_info:
                        authenticate_spotify_profile(
                            profile_name="test-profile",
                            settings=settings,
                            profiles=mock_profiles,
                            credentials=mock_credentials,
                            open_browser=False,
                        )

                    assert "missing 'id' field" in str(exc_info.value)

    def test_authenticate_spotify_profile_persists_token_metadata(self) -> None:
        """Test that token is persisted via KeyringCacheHandler and profile contains no tokens."""
        from playlist_bridge.auth.spotify import authenticate_spotify_profile
        from playlist_bridge.domain.models import AccountProfile

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        mock_token_info = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600,
        }

        mock_user_info = {
            "id": "test-user-id",
            "display_name": "Test User",
            "email": "test@example.com",
            "external_urls": {"spotify": "https://open.spotify.com/user/test-user-id"},
        }

        mock_saved_profile = MagicMock(spec=AccountProfile)
        mock_saved_profile.provider = "spotify"
        mock_saved_profile.account_id = "test-user-id"
        mock_saved_profile.display_name = "Test User"
        mock_saved_profile.email = "test@example.com"
        mock_saved_profile.profile_url = "https://open.spotify.com/user/test-user-id"

        # Track whether the cache handler was instantiated
        cache_handler_instantiated = False

        def cache_handler_side_effect(*args, **kwargs):
            nonlocal cache_handler_instantiated
            cache_handler_instantiated = True
            mock_handler = MagicMock(spec=KeyringCacheHandler)
            # Simulate that the cache handler saves the token
            return mock_handler

        with patch(
            "playlist_bridge.auth.spotify.KeyringCacheHandler",
            side_effect=cache_handler_side_effect,
        ) as mock_cache_handler_class:
            with patch(
                "playlist_bridge.auth.spotify.create_spotify_pkce_manager"
            ) as mock_create_manager:
                mock_pkce = MagicMock()
                mock_pkce.get_access_token.return_value = mock_token_info
                mock_create_manager.return_value = mock_pkce

                with patch("spotipy.Spotify") as mock_spotify_class:
                    mock_spotify_client = MagicMock()
                    mock_spotify_client.me.return_value = mock_user_info
                    mock_spotify_class.return_value = mock_spotify_client

                    mock_profiles.save.return_value = mock_saved_profile

                    result = authenticate_spotify_profile(
                        profile_name="test-profile",
                        settings=settings,
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                        open_browser=False,
                    )

        # Verify the cache handler was instantiated with the right arguments
        mock_cache_handler_class.assert_called_once_with(mock_credentials)
        assert cache_handler_instantiated is True

        # Verify the returned profile contains no tokens
        assert result == mock_saved_profile
        # The result should not contain access_token or refresh_token fields
        assert not hasattr(result, "access_token")
        assert not hasattr(result, "refresh_token")
        # The profile should have the expected metadata
        assert result.provider == "spotify"
        assert result.account_id == "test-user-id"
        assert result.display_name == "Test User"
        # Verify the profile model doesn't include token fields (structural check)
        # AccountProfile is a Pydantic model, check its field names
        profile_fields = set(AccountProfile.model_fields.keys())
        assert "access_token" not in profile_fields
        assert "refresh_token" not in profile_fields


class TestCreateAuthenticatedSpotifyClient:
    """Tests for create_authenticated_spotify_client function."""

    def test_creates_client_with_valid_token(self) -> None:
        """Test that a Spotify client is created when a valid token exists."""
        from playlist_bridge.settings import create_authenticated_spotify_client
        from playlist_bridge.providers.errors import AuthenticationRequired

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_credentials = MagicMock()
        mock_token_info = {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "expires_in": 3600,
        }

        with patch(
            "playlist_bridge.settings.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler = MagicMock()
            mock_cache_handler.get_cached_token.return_value = mock_token_info
            mock_cache_handler_class.return_value = mock_cache_handler

            with patch("playlist_bridge.settings.spotipy.Spotify") as mock_spotify_class:
                mock_spotify_client = MagicMock()
                mock_spotify_class.return_value = mock_spotify_client

                result = create_authenticated_spotify_client(
                    profile_name="test-profile",
                    settings=settings,
                    credentials=mock_credentials,
                )

                # Verify the cache handler was created with correct arguments
                mock_cache_handler_class.assert_called_once_with(
                    service="spotify",
                    profile_name="test-profile",
                    store=mock_credentials,
                )

                # Verify get_cached_token was called
                mock_cache_handler.get_cached_token.assert_called_once()

                # Verify Spotify client was created with the access token
                mock_spotify_class.assert_called_once_with(auth="mock-access-token")

                # Verify the result is the Spotify client
                assert result == mock_spotify_client

    def test_raises_authentication_required_when_no_token(self) -> None:
        """Test that AuthenticationRequired is raised when no token exists."""
        from playlist_bridge.settings import create_authenticated_spotify_client
        from playlist_bridge.providers.errors import AuthenticationRequired

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_credentials = MagicMock()

        with patch(
            "playlist_bridge.settings.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler = MagicMock()
            mock_cache_handler.get_cached_token.return_value = None
            mock_cache_handler_class.return_value = mock_cache_handler

            with pytest.raises(AuthenticationRequired) as exc_info:
                create_authenticated_spotify_client(
                    profile_name="test-profile",
                    settings=settings,
                    credentials=mock_credentials,
                )

            assert "No valid token found for profile 'test-profile'" in str(
                exc_info.value
            )

    def test_raises_authentication_required_when_token_missing_access_token(
        self,
    ) -> None:
        """Test that AuthenticationRequired is raised when token lacks access_token."""
        from playlist_bridge.settings import create_authenticated_spotify_client
        from playlist_bridge.providers.errors import AuthenticationRequired

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_credentials = MagicMock()
        mock_token_info = {"refresh_token": "mock-refresh-token"}  # No access_token

        with patch(
            "playlist_bridge.settings.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler = MagicMock()
            mock_cache_handler.get_cached_token.return_value = mock_token_info
            mock_cache_handler_class.return_value = mock_cache_handler

            with pytest.raises(AuthenticationRequired) as exc_info:
                create_authenticated_spotify_client(
                    profile_name="test-profile",
                    settings=settings,
                    credentials=mock_credentials,
                )

            assert "Token for profile 'test-profile' missing access_token" in str(
                exc_info.value
            )

    def test_raises_value_error_for_empty_profile_name(self) -> None:
        """Test that ValueError is raised when profile_name is empty."""
        from playlist_bridge.settings import create_authenticated_spotify_client

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_credentials = MagicMock()

        with pytest.raises(ValueError, match="profile_name must not be empty"):
            create_authenticated_spotify_client(
                profile_name="",
                settings=settings,
                credentials=mock_credentials,
            )

        with pytest.raises(ValueError, match="profile_name must not be empty"):
            create_authenticated_spotify_client(
                profile_name="   ",
                settings=settings,
                credentials=mock_credentials,
            )

    def test_raises_value_error_for_none_settings(self) -> None:
        """Test that ValueError is raised when settings is None."""
        from playlist_bridge.settings import create_authenticated_spotify_client

        mock_credentials = MagicMock()

        with pytest.raises(ValueError, match="settings must not be None"):
            create_authenticated_spotify_client(
                profile_name="test-profile",
                settings=None,  # type: ignore
                credentials=mock_credentials,
            )

    def test_raises_value_error_for_none_credentials(self) -> None:
        """Test that ValueError is raised when credentials is None."""
        from playlist_bridge.settings import create_authenticated_spotify_client

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )

        with pytest.raises(ValueError, match="credentials must not be None"):
            create_authenticated_spotify_client(
                profile_name="test-profile",
                settings=settings,
                credentials=None,  # type: ignore
            )

    def test_wraps_unexpected_errors_as_temporary_provider_failure(self) -> None:
        """Test that unexpected errors are wrapped as TemporaryProviderFailure."""
        from playlist_bridge.settings import create_authenticated_spotify_client
        from playlist_bridge.providers.errors import TemporaryProviderFailure

        settings = SpotifyOAuthSettings(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
        )
        mock_credentials = MagicMock()

        with patch(
            "playlist_bridge.settings.KeyringCacheHandler"
        ) as mock_cache_handler_class:
            mock_cache_handler = MagicMock()
            # Simulate an unexpected error when getting cached token
            mock_cache_handler.get_cached_token.side_effect = RuntimeError(
                "Unexpected error"
            )
            mock_cache_handler_class.return_value = mock_cache_handler

            with pytest.raises(TemporaryProviderFailure) as exc_info:
                create_authenticated_spotify_client(
                    profile_name="test-profile",
                    settings=settings,
                    credentials=mock_credentials,
                )

            assert "Failed to load Spotify token" in str(exc_info.value)
