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

        result = probe_spotify_identity(mock_client)

        assert isinstance(result, AccountProfile)
        assert result.provider == "spotify"
        assert result.account_id == "test-user-id-123"
        assert result.display_name == "Test User"
        assert result.email is None  # Email not stored in AccountProfile
        assert result.username == "Test User"
        assert result.profile_url == "https://open.spotify.com/user/test-user-id-123"
        mock_client.me.assert_called_once()

    def test_probe_spotify_identity_uses_display_name_fallback(self) -> None:
        """Test that display_name falls back to id if display_name is missing."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-456",
            "display_name": None,
        }

        result = probe_spotify_identity(mock_client)

        assert result.provider == "spotify"
        assert result.account_id == "test-user-id-456"
        assert result.display_name == "test-user-id-456"
        assert result.username is None
        assert result.profile_url is None

    def test_probe_spotify_identity_missing_id_raises_error(self) -> None:
        """Test that missing 'id' field raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "display_name": "Test User",
        }

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_spotify_identity(mock_client)

        assert "Spotify user profile missing 'id' field" in str(exc_info.value)
        assert exc_info.value.service == "spotify"
        assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_empty_response_raises_error(self) -> None:
        """Test that empty response raises InvalidProviderResponse."""
        mock_client = MagicMock()
        mock_client.me.return_value = None

        with pytest.raises(InvalidProviderResponse) as exc_info:
            probe_spotify_identity(mock_client)

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
                probe_spotify_identity(mock_client)

            assert exc_info.value.service == "spotify"
            assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_oauth_error_rate_limit_raises_rate_limited(self) -> None:
        """Test that rate limit OAuth error raises RateLimited."""
        mock_client = MagicMock()
        mock_client.me.side_effect = Exception("rate limit exceeded")

        with patch("playlist_bridge.auth.spotify.SpotifyOauthError", Exception):
            with pytest.raises(RateLimited) as exc_info:
                probe_spotify_identity(mock_client)

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
                probe_spotify_identity(mock_client)

            assert exc_info.value.service == "spotify"
            assert exc_info.value.operation == "probe_identity"

    def test_probe_spotify_identity_generic_exception_raises_temporary_failure(self) -> None:
        """Test that generic exceptions raise TemporaryProviderFailure."""
        mock_client = MagicMock()
        mock_client.me.side_effect = RuntimeError("Network timeout")

        with pytest.raises(TemporaryProviderFailure) as exc_info:
            probe_spotify_identity(mock_client)

        assert exc_info.value.service == "spotify"
        assert exc_info.value.operation == "probe_identity"
        assert "Spotify API temporarily unavailable" in str(exc_info.value)

    def test_probe_spotify_identity_handles_missing_display_name_field(self) -> None:
        """Test that missing display_name field uses id as fallback."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-789",
        }

        result = probe_spotify_identity(mock_client)

        assert result.account_id == "test-user-id-789"
        assert result.display_name == "test-user-id-789"
        assert result.username is None

    def test_probe_spotify_identity_handles_missing_external_urls(self) -> None:
        """Test that missing external_urls does not raise an error."""
        mock_client = MagicMock()
        mock_client.me.return_value = {
            "id": "test-user-id-101",
            "display_name": "Test User",
        }

        result = probe_spotify_identity(mock_client)

        assert result.profile_url is None


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

        result = probe_youtube_identity(mock_client)

        assert isinstance(result, AccountProfile)
        assert result.provider == "youtube"
        assert result.account_id == "UC123456789"
        assert result.display_name == "Test Channel"
        assert result.email is None
        assert result.username == "@testchannel"
        assert result.profile_url == "https://www.youtube.com/channel/UC123456789"

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

        result = probe_youtube_identity(mock_client)

        assert result.provider == "youtube"
        assert result.account_id == "UC987654321"
        assert result.display_name == "UC987654321"
        assert result.username is None
        assert result.profile_url == "https://www.youtube.com/channel/UC987654321"

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
            probe_youtube_identity(mock_client)

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
            probe_youtube_identity(mock_client)

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
            probe_youtube_identity(mock_client)

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
                probe_youtube_identity(mock_client)

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
                probe_youtube_identity(mock_client)

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
                probe_youtube_identity(mock_client)

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
                probe_youtube_identity(mock_client)

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
            probe_youtube_identity(mock_client)

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
