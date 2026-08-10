"""Tests for identity probing and status/logout functionality."""

from unittest.mock import MagicMock, patch

import pytest

from playlist_bridge.auth.spotify import probe_spotify_identity
from playlist_bridge.auth.youtube import probe_youtube_identity
from playlist_bridge.domain.models import AccountProfile
from playlist_bridge.providers.errors import (
    AuthenticationRequired,
    InvalidProviderResponse,
    PermissionDenied,
    RateLimited,
    TemporaryProviderFailure,
)


class TestProbeSpotifyIdentity:
    """Tests for probe_spotify_identity function."""

    def test_probe_spotify_identity_success(self) -> None:
        """Test successful identity probing returns AccountProfile."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-123",
            "display_name": "Test User",
            "email": "test@example.com",
            "external_urls": {"spotify": "https://open.spotify.com/user/test-user-id-123"},
        }

        result = probe_spotify_identity(mock_client, "test-profile")

        assert isinstance(result, AccountProfile)
        assert result.profile_name == "test-profile"
        assert result.service == "spotify"
        assert result.provider_user_id == "test-user-id-123"
        assert result.display_name == "Test User"
        mock_client.me.assert_called_once()

    def test_probe_spotify_identity_uses_display_name_fallback(self) -> None:
        """Test that display_name falls back to id if display_name is missing."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-456",
            "display_name": None,
        }

        result = probe_spotify_identity(mock_client, "test-profile")

        assert result.profile_name == "test-profile"
        assert result.service == "spotify"
        assert result.provider_user_id == "test-user-id-456"
        assert result.display_name == "test-user-id-456"

    def test_probe_spotify_identity_missing_id_raises_error(self) -> None:
        """Test that missing 'id' field raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "display_name": "Test User",
        }

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_spotify_identity(mock_client, "test-profile")

        assert "Spotify user profile missing 'id' field" in str(exc_info.value)
        assert exc_info.value.service == "spotify"
        assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_empty_response_raises_error(self) -> None:
        """Test that empty response raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_client.me.return_value = None

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_spotify_identity(mock_client, "test-profile")

        assert "Spotify returned empty user profile" in str(exc_info.value)
        assert exc_info.value.service == "spotify"
        assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_oauth_error_access_denied_raises_permission_denied(
        self,
    ) -> None:
        """Test that access_denied OAuth error raises PermissionDenied."""
        mock_client = MagicMock()
        mock_client.me.side_effect = Exception("access_denied")

        # Mock SpotifyOauthError to trigger the access_denied branch
        with patch("playlist_bridge.auth.spotify.SpotifyOauthError", Exception):
            with pytest.raises(PermissionDenied) as exc_info:
                probe_spotify_identity(mock_client, "test-profile")

            assert exc_info.value.service == "spotify"
            assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_oauth_error_rate_limit_raises_rate_limited(self) -> None:
        """Test that rate limit OAuth error raises RateLimited."""
        mock_client = MagicMock()
        mock_client.me.side_effect = Exception("rate limit exceeded")

        with patch("playlist_bridge.auth.spotify.SpotifyOauthError", Exception):
            with pytest.raises(RateLimited) as exc_info:
                probe_spotify_identity(mock_client, "test-profile")

            assert exc_info.value.service == "spotify"
            assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_other_oauth_error_raises_authentication_required(
        self,
    ) -> None:
        """Test that other OAuth errors raise AuthenticationRequired."""
        mock_client = MagicMock()
        mock_client.me.side_effect = Exception("invalid token")

        with patch("playlist_bridge.auth.spotify.SpotifyOauthError", Exception):
            with pytest.raises(AuthenticationRequired) as exc_info:
                probe_spotify_identity(mock_client, "test-profile")

            assert exc_info.value.service == "spotify"
            assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_generic_exception_raises_temporary_failure(self) -> None:
        """Test that generic exceptions raise TemporaryProviderFailure."""
        mock_client = MagicMock()
        mock_client.me.side_effect = RuntimeError("Network timeout")

        with pytest.raises(TemporaryProviderFailure) as exc_info:
            probe_spotify_identity(mock_client, "test-profile")

        assert exc_info.value.service == "spotify"
        assert exc_info.value.operation == "probe_identity"
        assert "Spotify API temporarily unavailable" in str(exc_info.value)

    def test_probe_spotify_identity_handles_missing_display_name_field(self) -> None:
        """Test that missing display_name field uses id as fallback."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-789",
        }

        result = probe_spotify_identity(mock_client, "test-profile")

        assert result.provider_user_id == "test-user-id-789"
        assert result.display_name == "test-user-id-789"

    def test_probe_spotify_identity_handles_missing_external_urls(self) -> None:
        """Test that missing external_urls does not raise an error."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-101",
            "display_name": "Test User",
        }

        result = probe_spotify_identity(mock_client, "test-profile")

        assert result.provider_user_id == "test-user-id-101"
        assert result.display_name == "Test User"
        assert result.service == "spotify"


class TestProbeYoutubeIdentity:
    """Tests for probe_youtube_identity function."""

    def test_probe_youtube_identity_success(self) -> None:
        """Test successful identity probing returns AccountProfile."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": "UC123456789",
                    "snippet": {
                        "title": "Test Channel",
                        "customUrl": "@testchannel",
                    },
                }
            ]
        }

        result = probe_youtube_identity(mock_client, "test-profile")

        assert isinstance(result, AccountProfile)
        assert result.profile_name == "test-profile"
        assert result.service == "youtube"
        assert result.provider_user_id == "UC123456789"
        assert result.display_name == "Test Channel"

        mock_client.channels.assert_called_once()
        mock_channels.list.assert_called_once_with(part="snippet", mine=True)
        mock_list.execute.assert_called_once()

    def test_probe_youtube_identity_uses_channel_id_fallback(self) -> None:
        """Test that display_name falls back to channel ID if title is missing."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": "UC987654321",
                    "snippet": {
                        "title": None,
                    },
                }
            ]
        }

        result = probe_youtube_identity(mock_client, "test-profile")

        assert result.profile_name == "test-profile"
        assert result.service == "youtube"
        assert result.provider_user_id == "UC987654321"
        assert result.display_name == "UC987654321"

    def test_probe_youtube_identity_missing_id_raises_error(self) -> None:
        """Test that missing 'id' field raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list
        mock_list.execute.return_value = {
            "items": [
                {
                    "id": None,
                    "snippet": {
                        "title": "Test Channel",
                    },
                }
            ]
        }

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_youtube_identity(mock_client, "test-profile")

        assert "YouTube channel missing 'id' field" in str(exc_info.value)
        assert exc_info.value.service == "youtube"
        assert exc_info.value.operation == "probe_identity"

    def test_probe_youtube_identity_empty_response_raises_error(self) -> None:
        """Test that empty response raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list
        mock_list.execute.return_value = None

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_youtube_identity(mock_client, "test-profile")

        assert "YouTube returned empty or invalid response" in str(exc_info.value)
        assert exc_info.value.service == "youtube"
        assert exc_info.value.operation == "probe_identity"

    def test_probe_youtube_identity_no_items_raises_error(self) -> None:
        """Test that no items in response raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list
        mock_list.execute.return_value = {"items": []}

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_youtube_identity(mock_client, "test-profile")

        assert "YouTube returned no channel data for authenticated user" in str(exc_info.value)
        assert exc_info.value.service == "youtube"
        assert exc_info.value.operation == "probe_identity"

    def test_probe_youtube_identity_http_401_raises_authentication_required(self) -> None:
        """Test that HTTP 401 error raises AuthenticationRequired."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list

        # Mock HttpError from googleapiclient.errors
        class MockHttpError(Exception):
            def __init__(self):
                self.resp = type("obj", (object,), {"status": 401})()

        with patch("googleapiclient.errors.HttpError", MockHttpError):
            mock_list.execute.side_effect = MockHttpError()

            with pytest.raises(AuthenticationRequired) as exc_info:
                probe_youtube_identity(mock_client, "test-profile")

            assert exc_info.value.service == "youtube"
            assert exc_info.value.operation == "probe_identity"
            assert "YouTube authentication required" in str(exc_info.value)

    def test_probe_youtube_identity_http_403_rate_limit_raises_rate_limited(self) -> None:
        """Test that HTTP 403 with rate limit message raises RateLimited."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list

        # Mock HttpError with rate limit message
        class MockHttpError(Exception):
            def __init__(self):
                self.resp = type("obj", (object,), {"status": 403})()
                self.error_details = {"errors": [{"reason": "rateLimitExceeded"}]}

            def __str__(self):
                return "Rate limit exceeded"

        with patch("googleapiclient.errors.HttpError", MockHttpError):
            mock_list.execute.side_effect = MockHttpError()

            with pytest.raises(RateLimited) as exc_info:
                probe_youtube_identity(mock_client, "test-profile")

            assert exc_info.value.service == "youtube"
            assert exc_info.value.operation == "probe_identity"
            assert "YouTube API rate limit exceeded" in str(exc_info.value)

    def test_probe_youtube_identity_http_403_permission_denied_raises_permission_denied(self) -> None:
        """Test that HTTP 403 without rate limit message raises PermissionDenied."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list

        # Mock HttpError with permission denied message
        class MockHttpError(Exception):
            def __init__(self):
                self.resp = type("obj", (object,), {"status": 403})()

            def __str__(self):
                return "Access denied"

        with patch("googleapiclient.errors.HttpError", MockHttpError):
            mock_list.execute.side_effect = MockHttpError()

            with pytest.raises(PermissionDenied) as exc_info:
                probe_youtube_identity(mock_client, "test-profile")

            assert exc_info.value.service == "youtube"
            assert exc_info.value.operation == "probe_identity"
            assert "User lacks permission to access YouTube profile" in str(exc_info.value)

    def test_probe_youtube_identity_http_404_raises_invalid_response(self) -> None:
        """Test that HTTP 404 error raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list

        # Mock HttpError with 404
        class MockHttpError(Exception):
            def __init__(self):
                self.resp = type("obj", (object,), {"status": 404})()

        with patch("googleapiclient.errors.HttpError", MockHttpError):
            mock_list.execute.side_effect = MockHttpError()

            with pytest.raises(InvalidProviderResponse) as exc_info:
                probe_youtube_identity(mock_client, "test-profile")

            assert exc_info.value.service == "youtube"
            assert exc_info.value.operation == "probe_identity"
            assert "YouTube channel not found" in str(exc_info.value)

    def test_probe_youtube_identity_generic_exception_raises_temporary_failure(self) -> None:
        """Test that generic exceptions raise TemporaryProviderFailure."""
        mock_client = MagicMock()
        mock_channels = MagicMock()
        mock_list = MagicMock()

        mock_client.channels.return_value = mock_channels
        mock_channels.list.return_value = mock_list
        mock_list.execute.side_effect = RuntimeError("Network timeout")

        # The RuntimeError will be caught by the final except block
        # and raised as TemporaryProviderFailure
        with pytest.raises(TemporaryProviderFailure) as exc_info:
            probe_youtube_identity(mock_client, "test-profile")

        assert exc_info.value.service == "youtube"
        assert exc_info.value.operation == "probe_identity"
        assert "YouTube API temporarily unavailable" in str(exc_info.value)


class TestAuthStatus:
    """Tests for AuthStatus model."""

    def test_auth_status_authenticated_serializes(self) -> None:
        """Test that authenticated status serializes correctly."""
        from playlist_bridge.auth.status import AuthStatus
        from playlist_bridge.domain.enums import SourceService

        status = AuthStatus(
            service=SourceService.YOUTUBE,
            profile_name="test-profile",
            state="authenticated",
            provider_user_id="user-123",
            display_name="Test User",
            safe_message="Authenticated successfully",
        )

        data = status.model_dump()
        assert data == {
            "service": "youtube",
            "profile_name": "test-profile",
            "state": "authenticated",
            "provider_user_id": "user-123",
            "display_name": "Test User",
            "safe_message": "Authenticated successfully",
        }

    def test_auth_status_missing_serializes(self) -> None:
        """Test that missing status serializes correctly."""
        from playlist_bridge.auth.status import AuthStatus
        from playlist_bridge.domain.enums import DestinationService

        status = AuthStatus(
            service=DestinationService.SPOTIFY,
            profile_name="missing-profile",
            state="missing",
            safe_message="No credentials found for this profile",
        )

        data = status.model_dump()
        assert data == {
            "service": "spotify",
            "profile_name": "missing-profile",
            "state": "missing",
            "provider_user_id": None,
            "display_name": None,
            "safe_message": "No credentials found for this profile",
        }

    def test_auth_status_expired_refreshable_serializes(self) -> None:
        """Test that expired_refreshable status serializes correctly."""
        from playlist_bridge.auth.status import AuthStatus
        from playlist_bridge.domain.enums import SourceService

        status = AuthStatus(
            service=SourceService.YOUTUBE,
            profile_name="expired-profile",
            state="expired_refreshable",
            safe_message="Token expired but refresh available",
        )

        data = status.model_dump()
        assert data == {
            "service": "youtube",
            "profile_name": "expired-profile",
            "state": "expired_refreshable",
            "provider_user_id": None,
            "display_name": None,
            "safe_message": "Token expired but refresh available",
        }

    def test_auth_status_invalid_serializes(self) -> None:
        """Test that invalid status serializes correctly."""
        from playlist_bridge.auth.status import AuthStatus
        from playlist_bridge.domain.enums import DestinationService

        status = AuthStatus(
            service=DestinationService.SPOTIFY,
            profile_name="invalid-profile",
            state="invalid",
            safe_message="Stored token is corrupted or invalid",
        )

        data = status.model_dump()
        assert data == {
            "service": "spotify",
            "profile_name": "invalid-profile",
            "state": "invalid",
            "provider_user_id": None,
            "display_name": None,
            "safe_message": "Stored token is corrupted or invalid",
        }

    def test_auth_status_rejects_extra_fields(self) -> None:
        """Test that AuthStatus rejects unknown fields."""
        from playlist_bridge.auth.status import AuthStatus
        from playlist_bridge.domain.enums import SourceService

        with pytest.raises(ValueError):
            AuthStatus(
                service=SourceService.YOUTUBE,
                profile_name="test",
                state="authenticated",
                unknown_field="should be rejected",  # type: ignore[arg-type]
            )

    def test_auth_status_rejects_invalid_state(self) -> None:
        """Test that AuthStatus rejects invalid state values."""
        from playlist_bridge.auth.status import AuthStatus
        from playlist_bridge.domain.enums import SourceService

        with pytest.raises(ValueError):
            AuthStatus(
                service=SourceService.YOUTUBE,
                profile_name="test",
                state="invalid_state",  # type: ignore[arg-type]
            )


class TestProbeSpotifyAuthStatus:
    """Tests for probe_spotify_auth_status function."""

    def test_probe_spotify_auth_status_missing_credentials(self) -> None:
        """Test that missing credentials returns 'missing' status."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from unittest.mock import MagicMock

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = None

        result = probe_spotify_auth_status(
            profile_name="test-profile",
            profiles=mock_profiles,
            credentials=mock_credentials,
        )

        assert isinstance(result, AuthStatus)
        assert result.service == DestinationService.SPOTIFY
        assert result.profile_name == "test-profile"
        assert result.state == "missing"
        assert result.safe_message == "No Spotify credentials found for this profile"
        assert result.provider_user_id is None
        assert result.display_name is None

    def test_probe_spotify_auth_status_authenticated(self) -> None:
        """Test that valid credentials return 'authenticated' status."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "valid-token",
            "refresh_token": "refresh-token",
        }

        # Mock the Spotify client and probe_spotify_identity
        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_profile = MagicMock()
            mock_profile.account_id = "user-123"
            mock_profile.display_name = "Test User"
            mock_probe.return_value = mock_profile

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert isinstance(result, AuthStatus)
                assert result.service == DestinationService.SPOTIFY
                assert result.profile_name == "test-profile"
                assert result.state == "authenticated"
                assert result.provider_user_id == "user-123"
                assert result.display_name == "Test User"
                assert result.safe_message == "Spotify authentication successful"

    def test_probe_spotify_auth_status_expired_refreshable(self) -> None:
        """Test that expired token with refresh returns 'expired_refreshable' status."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from playlist_bridge.providers.errors import AuthenticationRequired
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "expired-token",
            "refresh_token": "valid-refresh-token",
        }

        # Mock the Spotify client to raise AuthenticationRequired
        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_probe.side_effect = AuthenticationRequired(
                service="spotify",
                operation="probe_identity",
                safe_message="Token expired",
            )

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert isinstance(result, AuthStatus)
                assert result.service == DestinationService.SPOTIFY
                assert result.profile_name == "test-profile"
                assert result.state == "expired_refreshable"
                assert result.safe_message == "Token expired"
                assert result.provider_user_id is None
                assert result.display_name is None

    def test_probe_spotify_auth_status_invalid_no_access_token(self) -> None:
        """Test that credentials without access token but with refresh return 'expired_refreshable' status."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from unittest.mock import MagicMock

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "refresh_token": "refresh-token",
        }

        result = probe_spotify_auth_status(
            profile_name="test-profile",
            profiles=mock_profiles,
            credentials=mock_credentials,
        )

        assert isinstance(result, AuthStatus)
        assert result.service == DestinationService.SPOTIFY
        assert result.profile_name == "test-profile"
        assert result.state == "expired_refreshable"
        assert result.safe_message == "Spotify access token missing but refresh token available"
        assert result.provider_user_id is None
        assert result.display_name is None

    def test_probe_spotify_auth_status_invalid_no_refresh(self) -> None:
        """Test that invalid credentials without refresh return 'invalid' status."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from playlist_bridge.providers.errors import AuthenticationRequired
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "invalid-token",
        }

        # Mock the Spotify client to raise AuthenticationRequired
        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_probe.side_effect = AuthenticationRequired(
                service="spotify",
                operation="probe_identity",
                safe_message="Invalid token",
            )

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert isinstance(result, AuthStatus)
                assert result.service == DestinationService.SPOTIFY
                assert result.profile_name == "test-profile"
                assert result.state == "invalid"
                assert result.safe_message == "Invalid token"
                assert result.provider_user_id is None
                assert result.display_name is None

    def test_probe_spotify_auth_status_corruption_error(self) -> None:
        """Test that CredentialCorruptionError is raised when credentials are corrupted."""
        from playlist_bridge.auth.status import probe_spotify_auth_status
        from playlist_bridge.ports import CredentialCorruptionError
        from unittest.mock import MagicMock

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.side_effect = CredentialCorruptionError(
            service="spotify",
            profile_name="test-profile",
            safe_message="Corrupted token data",
        )

        with pytest.raises(CredentialCorruptionError) as exc_info:
            probe_spotify_auth_status(
                profile_name="test-profile",
                profiles=mock_profiles,
                credentials=mock_credentials,
            )

        assert exc_info.value.service == "spotify"
        assert exc_info.value.profile_name == "test-profile"
        assert "Corrupted token data" in str(exc_info.value)

    def test_probe_spotify_auth_status_permission_denied_with_refresh(self) -> None:
        """Test that PermissionDenied with refresh token returns 'expired_refreshable'."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from playlist_bridge.providers.errors import PermissionDenied
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "token",
            "refresh_token": "refresh-token",
        }

        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_probe.side_effect = PermissionDenied(
                service="spotify",
                operation="probe_identity",
                safe_message="Access denied",
            )

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert result.state == "expired_refreshable"
                assert "Access denied" in result.safe_message

    def test_probe_spotify_auth_status_permission_denied_no_refresh(self) -> None:
        """Test that PermissionDenied without refresh token returns 'invalid'."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from playlist_bridge.providers.errors import PermissionDenied
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "token",
        }

        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_probe.side_effect = PermissionDenied(
                service="spotify",
                operation="probe_identity",
                safe_message="Access denied",
            )

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert result.state == "invalid"
                assert "Access denied" in result.safe_message

    def test_probe_spotify_auth_status_rate_limited_with_refresh(self) -> None:
        """Test that RateLimited with refresh token returns 'expired_refreshable'."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from playlist_bridge.providers.errors import RateLimited
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "token",
            "refresh_token": "refresh-token",
        }

        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_probe.side_effect = RateLimited(
                service="spotify",
                operation="probe_identity",
                safe_message="Rate limit exceeded",
            )

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert result.state == "expired_refreshable"
                assert "Rate limit exceeded" in result.safe_message

    def test_probe_spotify_auth_status_unexpected_error(self) -> None:
        """Test that unexpected errors return 'invalid' status."""
        from playlist_bridge.auth.status import probe_spotify_auth_status, AuthStatus
        from playlist_bridge.domain.enums import DestinationService
        from unittest.mock import MagicMock, patch

        # Create mock repositories
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "access_token": "token",
            "refresh_token": "refresh-token",
        }

        with patch("playlist_bridge.auth.spotify.probe_spotify_identity") as mock_probe:
            mock_probe.side_effect = RuntimeError("Unexpected network error")

            with patch("spotipy.Spotify") as mock_spotify:
                mock_client = MagicMock()
                mock_spotify.return_value = mock_client

                result = probe_spotify_auth_status(
                    profile_name="test-profile",
                    profiles=mock_profiles,
                    credentials=mock_credentials,
                )

                assert result.state == "invalid"
                assert "Unexpected network error" in result.safe_message


class TestProbeYoutubeAuthStatus:
    """Tests for probe_youtube_auth_status function."""

    def test_probe_youtube_auth_status_missing_credentials(self) -> None:
        """Test that missing credentials returns 'missing' status."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = None

        result = probe_youtube_auth_status(
            profile_name="test-profile",
            profiles=mock_profiles,
            credentials=mock_credentials,
        )

        assert isinstance(result, AuthStatus)
        assert result.service == SourceService.YOUTUBE
        assert result.profile_name == "test-profile"
        assert result.state == "missing"
        assert result.safe_message == "No YouTube credentials found for this profile"
        assert result.provider_user_id is None
        assert result.display_name is None

    def test_probe_youtube_auth_status_authenticated(self) -> None:
        """Test that valid credentials return 'authenticated' status."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        # Provide properly structured credentials with a "token" field
        mock_credentials.load.return_value = {
            "token": "valid-token",
            "refresh_token": "refresh-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "valid-token"
            mock_creds.refresh_token = "refresh-token"
            mock_creds.valid = True
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                mock_profile = MagicMock()
                mock_profile.account_id = "channel-123"
                mock_profile.display_name = "Test Channel"
                mock_probe.return_value = mock_profile

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert isinstance(result, AuthStatus)
                    assert result.service == SourceService.YOUTUBE
                    assert result.profile_name == "test-profile"
                    assert result.state == "authenticated"
                    assert result.provider_user_id == "channel-123"
                    assert result.display_name == "Test Channel"
                    assert result.safe_message == "YouTube authentication successful"

    def test_probe_youtube_auth_status_expired_refreshable(self) -> None:
        """Test that expired token with refresh returns 'expired_refreshable' status."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from playlist_bridge.providers.errors import AuthenticationRequired
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "expired-token",
            "refresh_token": "refresh-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "expired-token"
            mock_creds.refresh_token = "refresh-token"
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                mock_probe.side_effect = AuthenticationRequired(
                    service="youtube",
                    operation="probe_identity",
                    safe_message="Token expired",
                )

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "expired_refreshable"
                    assert "Token expired" in result.safe_message

    def test_probe_youtube_auth_status_expired_no_refresh_returns_invalid(self) -> None:
        """Test that expired token without refresh returns 'invalid' status."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from playlist_bridge.providers.errors import AuthenticationRequired
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "expired-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "expired-token"
            mock_creds.refresh_token = None
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                mock_probe.side_effect = AuthenticationRequired(
                    service="youtube",
                    operation="probe_identity",
                    safe_message="Token expired, no refresh",
                )

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "invalid"
                    assert "Token expired, no refresh" in result.safe_message

    def test_probe_youtube_auth_status_invalid_credentials_returns_invalid(self) -> None:
        """Test that invalid credentials return 'invalid' status."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from playlist_bridge.providers.errors import PermissionDenied
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "invalid-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "invalid-token"
            mock_creds.refresh_token = None
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                mock_probe.side_effect = PermissionDenied(
                    service="youtube",
                    operation="probe_identity",
                    safe_message="Access denied",
                )

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "invalid"
                    assert "Access denied" in result.safe_message

    def test_probe_youtube_auth_status_rate_limited_with_refresh(self) -> None:
        """Test that RateLimited with refresh token returns 'expired_refreshable'."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from playlist_bridge.providers.errors import RateLimited
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "token",
            "refresh_token": "refresh-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "token"
            mock_creds.refresh_token = "refresh-token"
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                mock_probe.side_effect = RateLimited(
                    service="youtube",
                    operation="probe_identity",
                    safe_message="Rate limit exceeded",
                )

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "expired_refreshable"
                    assert "Rate limit exceeded" in result.safe_message

    def test_probe_youtube_auth_status_unexpected_error_returns_invalid(self) -> None:
        """Test that unexpected errors return 'invalid' status."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "token",
            "refresh_token": "refresh-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "token"
            mock_creds.refresh_token = "refresh-token"
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                mock_probe.side_effect = RuntimeError("Unexpected network error")

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "invalid"
                    assert "Unexpected network error" in result.safe_message

    def test_probe_youtube_auth_status_credential_corruption_propagates(self) -> None:
        """Test that CredentialCorruptionError is re-raised."""
        from playlist_bridge.auth.status import probe_youtube_auth_status
        from playlist_bridge.ports import CredentialCorruptionError
        from unittest.mock import MagicMock

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.side_effect = CredentialCorruptionError(
            service="youtube",
            profile_name="test-profile",
            safe_message="Corrupted credentials",
        )

        with pytest.raises(CredentialCorruptionError) as exc_info:
            probe_youtube_auth_status(
                profile_name="test-profile",
                profiles=mock_profiles,
                credentials=mock_credentials,
            )

        assert exc_info.value.service == "youtube"
        assert exc_info.value.profile_name == "test-profile"

    def test_probe_youtube_auth_status_http_401_with_refresh_returns_expired_refreshable(self) -> None:
        """Test that HTTP 401 with refresh token returns 'expired_refreshable'."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "token",
            "refresh_token": "refresh-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "token"
            mock_creds.refresh_token = "refresh-token"
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                # Simulate an HttpError with status 401
                class MockHttpError(Exception):
                    def __init__(self) -> None:
                        self.resp = MagicMock()
                        self.resp.status = 401

                mock_probe.side_effect = MockHttpError()

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "expired_refreshable"
                    assert "YouTube token expired but refresh available" in result.safe_message

    def test_probe_youtube_auth_status_http_401_no_refresh_returns_invalid(self) -> None:
        """Test that HTTP 401 without refresh token returns 'invalid'."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "token"
            mock_creds.refresh_token = None
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                class MockHttpError(Exception):
                    def __init__(self) -> None:
                        self.resp = MagicMock()
                        self.resp.status = 401

                mock_probe.side_effect = MockHttpError()

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "invalid"
                    assert "YouTube authentication required" in result.safe_message

    def test_probe_youtube_auth_status_http_403_rate_limit_with_refresh(self) -> None:
        """Test that HTTP 403 rate limit with refresh returns 'expired_refreshable'."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "token",
            "refresh_token": "refresh-token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "token"
            mock_creds.refresh_token = "refresh-token"
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                class MockHttpError(Exception):
                    def __init__(self) -> None:
                        self.resp = MagicMock()
                        self.resp.status = 403

                mock_probe.side_effect = MockHttpError()

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "expired_refreshable"
                    assert "YouTube API error: 403" in result.safe_message

    def test_probe_youtube_auth_status_http_403_no_refresh_returns_invalid(self) -> None:
        """Test that HTTP 403 without refresh token returns 'invalid'."""
        from playlist_bridge.auth.status import probe_youtube_auth_status, AuthStatus
        from playlist_bridge.domain.enums import SourceService
        from unittest.mock import MagicMock, patch

        mock_profiles = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.load.return_value = {
            "token": "token",
        }

        # Mock deserialize_google_credentials to avoid real validation
        with patch("playlist_bridge.auth.youtube.deserialize_google_credentials") as mock_deserialize:
            mock_creds = MagicMock()
            mock_creds.token = "token"
            mock_creds.refresh_token = None
            mock_deserialize.return_value = mock_creds

            with patch("playlist_bridge.auth.youtube.probe_youtube_identity") as mock_probe:
                class MockHttpError(Exception):
                    def __init__(self) -> None:
                        self.resp = MagicMock()
                        self.resp.status = 403

                mock_probe.side_effect = MockHttpError()

                with patch("googleapiclient.discovery.build") as mock_build:
                    mock_client = MagicMock()
                    mock_build.return_value = mock_client

                    result = probe_youtube_auth_status(
                        profile_name="test-profile",
                        profiles=mock_profiles,
                        credentials=mock_credentials,
                    )

                    assert result.state == "invalid"
                    assert "YouTube API error: 403" in result.safe_message
