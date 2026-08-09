"""Unit tests for YouTube/Google authentication utilities."""

import json
import tempfile
import unittest
from pathlib import Path

import pytest
from google.oauth2.credentials import Credentials

from playlist_bridge.auth.youtube import (
    DEFAULT_REDIRECT_HOST,
    DEFAULT_REDIRECT_PORT,
    DEFAULT_YOUTUBE_SCOPES,
    deserialize_google_credentials,
    load_google_client_config,
    serialize_google_credentials,
)
from playlist_bridge.ports import CredentialCorruptionError
from playlist_bridge.settings import GoogleOAuthSettings


class TestGoogleOAuthSettings:
    """Tests for the GoogleOAuthSettings model."""

    def test_google_oauth_settings_creation_with_valid_path(self) -> None:
        """Test that GoogleOAuthSettings creates successfully with a valid file path."""
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            settings = GoogleOAuthSettings(client_secret_path=path)
            assert settings.client_secret_path == path
            assert settings.scopes == DEFAULT_YOUTUBE_SCOPES
            assert settings.redirect_host == DEFAULT_REDIRECT_HOST
            assert settings.redirect_port == DEFAULT_REDIRECT_PORT

    def test_google_oauth_settings_fails_with_nonexistent_path(self) -> None:
        """Test that GoogleOAuthSettings raises ValueError for a nonexistent file."""
        nonexistent_path = Path("/tmp/nonexistent_client_secret.json")
        with pytest.raises(ValueError, match=r"Google client secret file not found"):
            GoogleOAuthSettings(client_secret_path=nonexistent_path)

    def test_google_oauth_settings_fails_with_directory_path(self) -> None:
        """Test that GoogleOAuthSettings raises ValueError when path is a directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            dir_path = Path(tmp_dir)
            with pytest.raises(ValueError, match=r"Google client secret path is not a file"):
                GoogleOAuthSettings(client_secret_path=dir_path)

    def test_google_oauth_settings_with_custom_scopes(self) -> None:
        """Test that GoogleOAuthSettings accepts custom scopes."""
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            custom_scopes = ("https://www.googleapis.com/auth/youtube.readonly",)
            settings = GoogleOAuthSettings(
                client_secret_path=path,
                scopes=custom_scopes,
                redirect_host="127.0.0.1",
                redirect_port=9000,
            )
            assert settings.scopes == custom_scopes
            assert settings.redirect_host == "127.0.0.1"
            assert settings.redirect_port == 9000


class TestLoadGoogleClientConfig:
    """Tests for the load_google_client_config function."""

    def test_load_google_client_config_with_valid_path(self) -> None:
        """Test that load_google_client_config returns GoogleOAuthSettings for a valid file."""
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            settings = load_google_client_config(path)
            assert isinstance(settings, GoogleOAuthSettings)
            assert settings.client_secret_path == path
            assert settings.scopes == DEFAULT_YOUTUBE_SCOPES
            assert settings.redirect_host == DEFAULT_REDIRECT_HOST
            assert settings.redirect_port == DEFAULT_REDIRECT_PORT

    def test_load_google_client_config_raises_file_not_found_for_missing(self) -> None:
        """Test that load_google_client_config raises FileNotFoundError for missing path."""
        nonexistent_path = Path("/tmp/missing_client_secret.json")
        with pytest.raises(FileNotFoundError, match=r"Google client secret file not found"):
            load_google_client_config(nonexistent_path)

    def test_load_google_client_config_raises_value_error_for_directory(self) -> None:
        """Test that load_google_client_config raises ValueError when path is a directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            dir_path = Path(tmp_dir)
            with pytest.raises(ValueError, match=r"Google client secret path is not a file"):
                load_google_client_config(dir_path)

    def test_load_google_client_config_works_with_actual_json_file(self) -> None:
        """Test that load_google_client_config works with an actual JSON file.

        Note: This test creates a valid-looking JSON file, but doesn't parse the
        JSON content since the function only validates the file existence.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as tmp:
            # Write some JSON content (not actually parsed by the function)
            json.dump({"installed": {"client_id": "test"}}, tmp)
            tmp.flush()
            path = Path(tmp.name)
            settings = load_google_client_config(path)
            assert isinstance(settings, GoogleOAuthSettings)
            assert settings.client_secret_path == path

    def test_load_google_client_config_returns_defaults(self) -> None:
        """Test that load_google_client_config returns default OAuth configuration."""
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            settings = load_google_client_config(path)
            # Verify defaults match the constants
            assert settings.scopes == DEFAULT_YOUTUBE_SCOPES
            assert settings.redirect_host == DEFAULT_REDIRECT_HOST
            assert settings.redirect_port == DEFAULT_REDIRECT_PORT
            # Verify the scopes contain expected values
            assert "https://www.googleapis.com/auth/youtube" in settings.scopes
            assert "https://www.googleapis.com/auth/youtube.force-ssl" in settings.scopes
            assert "https://www.googleapis.com/auth/youtube.readonly" in settings.scopes

    def test_load_google_client_config_integration_with_oauth_settings(self) -> None:
        """Integration test: load_google_client_config creates a valid GoogleOAuthSettings instance.

        This test verifies that the returned GoogleOAuthSettings instance can be
        used for OAuth configuration without raising validation errors.
        """
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            settings = load_google_client_config(path)
            # The settings object should be fully validated and ready for use
            # in the OAuth flow (the actual flow will parse the JSON file)
            assert settings.client_secret_path == path
            # Ensure the validation passes (no exception)
            settings.model_post_init(None)

    def test_load_google_client_config_handles_empty_file(self) -> None:
        """Test that load_google_client_config works with empty files.

        Note: The function only validates existence and file type, not content.
        The JSON parsing is deferred to google-auth-oauthlib.
        """
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            settings = load_google_client_config(path)
            assert isinstance(settings, GoogleOAuthSettings)
            # The file exists and is a file, so the function succeeds
            assert settings.client_secret_path == path


class TestGoogleCredentialSerialization:
    """Tests for serializing and deserializing Google credentials."""

    def test_serialize_google_credentials_minimal(self) -> None:
        """Test serializing a minimal Credentials object with only a token."""
        creds = Credentials(token="test_token_123")
        serialized = serialize_google_credentials(creds)
        data = json.loads(serialized)
        assert data["token"] == "test_token_123"
        assert "refresh_token" not in data
        assert "token_uri" not in data
        assert "client_id" not in data
        assert "client_secret" not in data
        assert "scopes" not in data

    def test_serialize_google_credentials_full(self) -> None:
        """Test serializing a fully-populated Credentials object."""
        creds = Credentials(
            token="token_abc",
            refresh_token="refresh_xyz",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="client_123",
            client_secret="secret_456",
            scopes=["https://www.googleapis.com/auth/youtube"],
        )
        serialized = serialize_google_credentials(creds)
        data = json.loads(serialized)
        assert data["token"] == "token_abc"
        assert data["refresh_token"] == "refresh_xyz"
        assert data["token_uri"] == "https://oauth2.googleapis.com/token"
        assert data["client_id"] == "client_123"
        assert data["client_secret"] == "secret_456"
        assert data["scopes"] == ["https://www.googleapis.com/auth/youtube"]

    def test_serialize_google_credentials_handles_missing_fields(self) -> None:
        """Test serialization when optional fields are None."""
        creds = Credentials(
            token="token_abc",
            refresh_token=None,
            token_uri=None,
            client_id=None,
            client_secret=None,
            scopes=[],
        )
        serialized = serialize_google_credentials(creds)
        data = json.loads(serialized)
        assert data["token"] == "token_abc"
        assert "refresh_token" not in data
        assert "token_uri" not in data
        assert "client_id" not in data
        assert "client_secret" not in data
        assert "scopes" not in data

    def test_serialize_google_credentials_raises_on_missing_token(self) -> None:
        """Test that serialization raises when the credentials object has no token."""
        creds = Credentials(token=None)
        with pytest.raises(CredentialCorruptionError, match="youtube"):
            serialize_google_credentials(creds)

    def test_deserialize_google_credentials_minimal(self) -> None:
        """Test deserializing a minimal credential payload."""
        serialized = json.dumps({"token": "test_token_123"})
        scopes = ["https://www.googleapis.com/auth/youtube"]
        creds = deserialize_google_credentials(serialized, scopes)
        assert creds.token == "test_token_123"
        assert creds.refresh_token is None
        assert creds.token_uri is None
        assert creds.client_id is None
        assert creds.client_secret is None
        assert creds.scopes == ["https://www.googleapis.com/auth/youtube"]

    def test_deserialize_google_credentials_full(self) -> None:
        """Test deserializing a fully-populated credential payload."""
        payload = {
            "token": "token_abc",
            "refresh_token": "refresh_xyz",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_123",
            "client_secret": "secret_456",
            "scopes": ["https://www.googleapis.com/auth/youtube"],
        }
        serialized = json.dumps(payload)
        scopes = []  # Should be ignored because payload has scopes
        creds = deserialize_google_credentials(serialized, scopes)
        assert creds.token == "token_abc"
        assert creds.refresh_token == "refresh_xyz"
        assert creds.token_uri == "https://oauth2.googleapis.com/token"
        assert creds.client_id == "client_123"
        assert creds.client_secret == "secret_456"
        assert creds.scopes == ["https://www.googleapis.com/auth/youtube"]

    def test_deserialize_google_credentials_fallback_scopes(self) -> None:
        """Test that deserialization uses provided scopes when payload lacks them."""
        serialized = json.dumps({"token": "test_token"})
        scopes = ["scope1", "scope2"]
        creds = deserialize_google_credentials(serialized, scopes)
        assert creds.scopes == ["scope1", "scope2"]

    def test_deserialize_google_credentials_empty_scopes(self) -> None:
        """Test that deserialization handles empty scopes list."""
        payload = {"token": "test_token", "scopes": []}
        serialized = json.dumps(payload)
        scopes = ["default_scope"]
        creds = deserialize_google_credentials(serialized, scopes)
        assert creds.scopes == []

    def test_deserialize_google_credentials_raises_on_bad_json(self) -> None:
        """Test that deserialization raises on malformed JSON."""
        with pytest.raises(CredentialCorruptionError, match="Malformed JSON"):
            deserialize_google_credentials("{not valid json}", [])

    def test_deserialize_google_credentials_raises_on_missing_token(self) -> None:
        """Test that deserialization raises when token field is missing."""
        serialized = json.dumps({"refresh_token": "some_token"})
        with pytest.raises(CredentialCorruptionError, match="Missing or invalid token field"):
            deserialize_google_credentials(serialized, [])

    def test_deserialize_google_credentials_raises_on_non_string_token(self) -> None:
        """Test that deserialization raises when token is not a string."""
        serialized = json.dumps({"token": 12345})
        with pytest.raises(CredentialCorruptionError, match="Missing or invalid token field"):
            deserialize_google_credentials(serialized, [])

    def test_deserialize_google_credentials_raises_on_invalid_scopes_type(self) -> None:
        """Test that deserialization raises when scopes is not a list."""
        serialized = json.dumps({"token": "test", "scopes": "not_a_list"})
        with pytest.raises(CredentialCorruptionError, match="scopes field must be a list"):
            deserialize_google_credentials(serialized, [])

    def test_deserialize_google_credentials_raises_on_invalid_scopes_content(self) -> None:
        """Test that deserialization raises when scopes contains non-strings."""
        serialized = json.dumps({"token": "test", "scopes": [1, 2, 3]})
        with pytest.raises(CredentialCorruptionError, match="scopes field must contain only strings"):
            deserialize_google_credentials(serialized, [])

    def test_serialize_deserialize_round_trip(self) -> None:
        """Test that serialize and deserialize are inverses."""
        original = Credentials(
            token="token_round",
            refresh_token="refresh_round",
            token_uri="https://oauth2.googleapis.com/token",
            client_id="client_round",
            client_secret="secret_round",
            scopes=["scope1", "scope2"],
        )
        serialized = serialize_google_credentials(original)
        reconstructed = deserialize_google_credentials(serialized, [])
        assert reconstructed.token == original.token
        assert reconstructed.refresh_token == original.refresh_token
        assert reconstructed.token_uri == original.token_uri
        assert reconstructed.client_id == original.client_id
        assert reconstructed.client_secret == original.client_secret
        assert reconstructed.scopes == original.scopes

    def test_serialize_google_credentials_uses_sort_keys_and_compact_format(self) -> None:
        """Test that serialization produces compact, sorted JSON."""
        creds = Credentials(
            token="token_a",
            refresh_token="refresh_a",
            client_id="client_a",
            token_uri="https://token.uri",
            client_secret="secret_a",
        )
        serialized = serialize_google_credentials(creds)
        # Should be compact (no spaces) and have keys sorted alphabetically
        assert ' ' not in serialized
        data = json.loads(serialized)
        # Check that keys are sorted alphabetically in the output
        keys = list(data.keys())
        assert keys == sorted(keys)

    def test_deserialize_google_credentials_handles_none_refresh_token(self) -> None:
        """Test deserialization when refresh_token is explicitly null."""
        payload = {"token": "test", "refresh_token": None}
        serialized = json.dumps(payload)
        creds = deserialize_google_credentials(serialized, [])
        assert creds.refresh_token is None

    def test_deserialize_google_credentials_handles_none_token_uri(self) -> None:
        """Test deserialization when token_uri is explicitly null."""
        payload = {"token": "test", "token_uri": None}
        serialized = json.dumps(payload)
        creds = deserialize_google_credentials(serialized, [])
        assert creds.token_uri is None


class TestYouTubeAuthConstants:
    """Tests for YouTube authentication constants."""

    def test_default_scopes_are_defined(self) -> None:
        """Test that DEFAULT_YOUTUBE_SCOPES is a tuple of strings."""
        assert isinstance(DEFAULT_YOUTUBE_SCOPES, tuple)
        assert all(isinstance(scope, str) for scope in DEFAULT_YOUTUBE_SCOPES)
        assert len(DEFAULT_YOUTUBE_SCOPES) >= 3

    def test_default_scopes_include_required_scopes(self) -> None:
        """Test that DEFAULT_YOUTUBE_SCOPES includes required YouTube scopes."""
        required_scopes = [
            "https://www.googleapis.com/auth/youtube",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.readonly",
        ]
        for scope in required_scopes:
            assert scope in DEFAULT_YOUTUBE_SCOPES

    def test_default_redirect_host_is_defined(self) -> None:
        """Test that DEFAULT_REDIRECT_HOST is a string."""
        assert isinstance(DEFAULT_REDIRECT_HOST, str)
        assert DEFAULT_REDIRECT_HOST == "localhost"

    def test_default_redirect_port_is_defined(self) -> None:
        """Test that DEFAULT_REDIRECT_PORT is an integer."""
        assert isinstance(DEFAULT_REDIRECT_PORT, int)
        assert DEFAULT_REDIRECT_PORT == 8080


class TestRefreshGoogleCredentials:
    """Tests for the refresh_google_credentials function."""

    def test_refresh_google_credentials_returns_valid_credentials_when_not_expired(
        self,
    ) -> None:
        """Test that refresh returns the stored credentials without refreshing if not expired."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import refresh_google_credentials
        from playlist_bridge.domain.enums import SourceService

        # Create a mock credential store
        mock_store = MagicMock()
        mock_store.load.return_value = {
            "token": "valid_token",
            "refresh_token": "refresh_token_123",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_123",
            "client_secret": "secret_456",
            "scopes": ["https://www.googleapis.com/auth/youtube"],
        }

        # Create a mock Request object
        mock_request = MagicMock()

        # Create a mock credentials object with expired=False
        from google.oauth2.credentials import Credentials

        # Create a MagicMock that behaves like Credentials
        mock_creds = MagicMock(spec=Credentials)
        # Set the attributes that will be accessed
        type(mock_creds).expired = unittest.mock.PropertyMock(return_value=False)
        mock_creds.token = "valid_token"
        mock_creds.refresh_token = "refresh_token_123"
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = "client_123"
        mock_creds.client_secret = "secret_456"
        mock_creds.scopes = ["https://www.googleapis.com/auth/youtube"]

        # Mock the Credentials constructor to return our mock
        with unittest.mock.patch(
            "playlist_bridge.auth.youtube.Credentials",
            return_value=mock_creds,
        ):
            result = refresh_google_credentials("test_profile", mock_store, mock_request)

            # Should return the credentials without refreshing
            assert result is mock_creds
            # Should not have called refresh or save
            mock_creds.refresh.assert_not_called()
            mock_store.save.assert_not_called()

    def test_refresh_google_credentials_refreshes_expired_credentials_and_saves(
        self,
    ) -> None:
        """Test that refresh refreshes expired credentials and writes the new payload once."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import refresh_google_credentials
        from playlist_bridge.domain.enums import SourceService

        # Create a mock credential store
        mock_store = MagicMock()
        mock_store.load.return_value = {
            "token": "expired_token",
            "refresh_token": "refresh_token_123",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client_123",
            "client_secret": "secret_456",
            "scopes": ["https://www.googleapis.com/auth/youtube"],
        }

        # Create a mock Request object
        mock_request = MagicMock()

        # Create a mock credentials object with expired=True
        from google.oauth2.credentials import Credentials

        mock_creds = MagicMock(spec=Credentials)
        # Set the attributes that will be accessed
        type(mock_creds).expired = unittest.mock.PropertyMock(return_value=True)
        mock_creds.token = "expired_token"
        mock_creds.refresh_token = "refresh_token_123"
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = "client_123"
        mock_creds.client_secret = "secret_456"
        mock_creds.scopes = ["https://www.googleapis.com/auth/youtube"]

        # Mock the refresh method to update the token
        def refresh_side_effect(request):
            mock_creds.token = "new_refreshed_token"

        mock_creds.refresh = MagicMock(side_effect=refresh_side_effect)

        # Mock the Credentials constructor to return our mock
        with unittest.mock.patch(
            "playlist_bridge.auth.youtube.Credentials",
            return_value=mock_creds,
        ):
            # Mock serialize_google_credentials to return serialized payload
            with unittest.mock.patch(
                "playlist_bridge.auth.youtube.serialize_google_credentials",
                return_value=json.dumps(
                    {
                        "token": "new_refreshed_token",
                        "refresh_token": "refresh_token_123",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "client_id": "client_123",
                        "client_secret": "secret_456",
                        "scopes": ["https://www.googleapis.com/auth/youtube"],
                    }
                ),
            ):
                result = refresh_google_credentials("test_profile", mock_store, mock_request)

                # Should have called refresh
                mock_creds.refresh.assert_called_once_with(mock_request)
                # Should have saved the refreshed credentials
                mock_store.save.assert_called_once()
                # The save should be called with the correct service and payload
                call_args = mock_store.save.call_args
                assert call_args[0][0] == SourceService.YOUTUBE
                assert call_args[0][1] == "test_profile"
                payload = call_args[0][2]
                assert payload["token"] == "new_refreshed_token"
                # Should return the refreshed credentials
                assert result is mock_creds
                assert result.token == "new_refreshed_token"


class TestAuthenticateYouTubeProfile:
    """Tests for the authenticate_youtube_profile function."""

    def test_authenticate_youtube_profile_success(self) -> None:
        """Test that authenticate_youtube_profile successfully authenticates and stores credentials."""
        import json
        from unittest.mock import MagicMock, patch

        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.domain.enums import SourceService
        from playlist_bridge.settings import GoogleOAuthSettings

        # Create a mock settings object
        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = True
        mock_settings.scopes = ("https://www.googleapis.com/auth/youtube",)
        mock_settings.redirect_host = "localhost"
        mock_settings.redirect_port = 8080

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        # Create mock credentials
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.token = "test_token_123"
        mock_creds.refresh_token = "test_refresh_token"
        mock_creds.token_uri = "https://oauth2.googleapis.com/token"
        mock_creds.client_id = "test_client_id"
        mock_creds.client_secret = "test_client_secret"
        mock_creds.scopes = ["https://www.googleapis.com/auth/youtube"]

        # Create a mock flow
        mock_flow = MagicMock(spec=InstalledAppFlow)
        mock_flow.run_local_server.return_value = mock_creds

        # Create a mock YouTube client
        mock_youtube = MagicMock()
        mock_profile = AccountProfile(
            profile_name="test-profile",
            service="youtube",
            provider_user_id="channel_123",
            display_name="Test Channel",
        )

        with patch("playlist_bridge.auth.youtube.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow):
            with patch("playlist_bridge.auth.youtube.serialize_google_credentials", return_value=json.dumps({
                "token": "test_token_123",
                "refresh_token": "test_refresh_token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "scopes": ["https://www.googleapis.com/auth/youtube"],
            })):
                with patch("playlist_bridge.auth.youtube.build") as mock_build:
                    mock_build.return_value = mock_youtube
                    with patch("playlist_bridge.auth.youtube.probe_youtube_identity", return_value=mock_profile):
                        result = authenticate_youtube_profile(
                            profile_name="test-profile",
                            settings=mock_settings,
                            profiles=mock_profiles,
                            credentials=mock_credentials,
                            open_browser=True,
                        )

                        # Verify the flow was created with the correct parameters
                        mock_flow.run_local_server.assert_called_once_with(
                            host="localhost",
                            port=8080,
                            open_browser=True,
                        )

                        # Verify credentials were saved
                        mock_credentials.save.assert_called_once()
                        call_args = mock_credentials.save.call_args
                        assert call_args[0][0] == SourceService.YOUTUBE
                        assert call_args[0][1] == "test-profile"
                        payload = call_args[0][2]
                        assert payload["token"] == "test_token_123"

                        # Verify profile was saved
                        mock_profiles.save.assert_called_once()
                        saved_profile = mock_profiles.save.call_args[0][0]
                        assert saved_profile.profile_name == "test-profile"
                        assert saved_profile.service == "youtube"
                        assert saved_profile.provider_user_id == "channel_123"
                        assert saved_profile.display_name == "Test Channel"

                        # Verify the result
                        assert result is saved_profile

    def test_authenticate_youtube_profile_missing_client_secret(self) -> None:
        """Test that authenticate_youtube_profile raises ValueError when client secret is missing."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.settings import GoogleOAuthSettings

        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = False

        with pytest.raises(ValueError, match="Google client secret file not found"):
            authenticate_youtube_profile(
                profile_name="test-profile",
                settings=mock_settings,
                profiles=MagicMock(),
                credentials=MagicMock(),
                open_browser=True,
            )

    def test_authenticate_youtube_profile_empty_profile_name(self) -> None:
        """Test that authenticate_youtube_profile raises ValueError when profile_name is empty."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import authenticate_youtube_profile

        with pytest.raises(ValueError, match="profile_name must not be empty"):
            authenticate_youtube_profile(
                profile_name="",
                settings=MagicMock(),
                profiles=MagicMock(),
                credentials=MagicMock(),
                open_browser=True,
            )

    def test_authenticate_youtube_profile_none_settings(self) -> None:
        """Test that authenticate_youtube_profile raises ValueError when settings is None."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import authenticate_youtube_profile

        with pytest.raises(ValueError, match="settings must not be None"):
            authenticate_youtube_profile(
                profile_name="test-profile",
                settings=None,
                profiles=MagicMock(),
                credentials=MagicMock(),
                open_browser=True,
            )

    def test_authenticate_youtube_profile_none_profiles(self) -> None:
        """Test that authenticate_youtube_profile raises ValueError when profiles is None."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.settings import GoogleOAuthSettings

        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = True

        with pytest.raises(ValueError, match="profiles repository must not be None"):
            authenticate_youtube_profile(
                profile_name="test-profile",
                settings=mock_settings,
                profiles=None,
                credentials=MagicMock(),
                open_browser=True,
            )

    def test_authenticate_youtube_profile_none_credentials(self) -> None:
        """Test that authenticate_youtube_profile raises ValueError when credentials is None."""
        from unittest.mock import MagicMock

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.settings import GoogleOAuthSettings

        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = True

        with pytest.raises(ValueError, match="credentials store must not be None"):
            authenticate_youtube_profile(
                profile_name="test-profile",
                settings=mock_settings,
                profiles=MagicMock(),
                credentials=None,
                open_browser=True,
            )

    def test_authenticate_youtube_profile_flow_failure(self) -> None:
        """Test that authenticate_youtube_profile raises AuthenticationRequired when flow fails."""
        import json
        from unittest.mock import MagicMock, patch

        from google_auth_oauthlib.flow import InstalledAppFlow

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.settings import GoogleOAuthSettings

        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = True
        mock_settings.scopes = ("https://www.googleapis.com/auth/youtube",)
        mock_settings.redirect_host = "localhost"
        mock_settings.redirect_port = 8080

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        mock_flow = MagicMock(spec=InstalledAppFlow)
        mock_flow.run_local_server.side_effect = Exception("OAuth flow failed")

        with patch("playlist_bridge.auth.youtube.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow):
            with pytest.raises(AuthenticationRequired, match="Authentication failed"):
                authenticate_youtube_profile(
                    profile_name="test-profile",
                    settings=mock_settings,
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                    open_browser=True,
                )

    def test_authenticate_youtube_profile_access_denied(self) -> None:
        """Test that authenticate_youtube_profile raises PermissionDenied when user denies access."""
        from unittest.mock import MagicMock, patch

        from google_auth_oauthlib.flow import InstalledAppFlow

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.settings import GoogleOAuthSettings

        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = True
        mock_settings.scopes = ("https://www.googleapis.com/auth/youtube",)
        mock_settings.redirect_host = "localhost"
        mock_settings.redirect_port = 8080

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        mock_flow = MagicMock(spec=InstalledAppFlow)
        # Simulate an access denied error
        mock_flow.run_local_server.side_effect = Exception("access_denied")

        with patch("playlist_bridge.auth.youtube.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow):
            with pytest.raises(PermissionDenied, match="User denied permission"):
                authenticate_youtube_profile(
                    profile_name="test-profile",
                    settings=mock_settings,
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                    open_browser=True,
                )

    def test_authenticate_youtube_profile_invalid_client(self) -> None:
        """Test that authenticate_youtube_profile raises AuthenticationRequired when client is invalid."""
        from unittest.mock import MagicMock, patch

        from google_auth_oauthlib.flow import InstalledAppFlow

        from playlist_bridge.auth.youtube import authenticate_youtube_profile
        from playlist_bridge.settings import GoogleOAuthSettings

        mock_settings = MagicMock(spec=GoogleOAuthSettings)
        mock_settings.client_secret_path = MagicMock()
        mock_settings.client_secret_path.exists.return_value = True
        mock_settings.scopes = ("https://www.googleapis.com/auth/youtube",)
        mock_settings.redirect_host = "localhost"
        mock_settings.redirect_port = 8080

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        mock_flow = MagicMock(spec=InstalledAppFlow)
        # Simulate an invalid client error
        mock_flow.run_local_server.side_effect = Exception("invalid_client")

        with patch("playlist_bridge.auth.youtube.InstalledAppFlow.from_client_secrets_file", return_value=mock_flow):
            with pytest.raises(AuthenticationRequired, match="Invalid Google client configuration"):
                authenticate_youtube_profile(
                    profile_name="test-profile",
                    settings=mock_settings,
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                    open_browser=True,
                )
