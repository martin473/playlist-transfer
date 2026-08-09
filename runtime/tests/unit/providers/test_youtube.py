"""Unit tests for YouTube provider utilities."""

import pytest

from playlist_bridge.providers.youtube import (
    parse_youtube_duration_ms,
    parse_youtube_playlist_id,
    fetch_youtube_playlist_metadata,
)
from playlist_bridge.providers.errors import (
    AuthenticationRequired,
    PermissionDenied,
    ProviderNotFound,
    RateLimited,
    InvalidProviderResponse,
    TemporaryProviderFailure,
)
from playlist_bridge.domain.models import PlaylistReference, SourcePlaylistMetadata


class TestParseYouTubePlaylistId:
    """Tests for parse_youtube_playlist_id function."""

    def test_valid_standard_youtube_playlist(self) -> None:
        """Test parsing a standard YouTube playlist URL."""
        url = "https://www.youtube.com/playlist?list=PL1234567890"
        assert parse_youtube_playlist_id(url) == "PL1234567890"

    def test_valid_youtube_music_playlist(self) -> None:
        """Test parsing a YouTube Music playlist URL."""
        url = "https://music.youtube.com/playlist?list=PL9876543210"
        assert parse_youtube_playlist_id(url) == "PL9876543210"

    def test_valid_playlist_with_additional_params(self) -> None:
        """Test parsing a playlist URL with additional query parameters."""
        url = "https://www.youtube.com/playlist?list=PL123&index=1&t=0"
        assert parse_youtube_playlist_id(url) == "PL123"

    def test_valid_video_in_playlist_url(self) -> None:
        """Test parsing a video URL with a playlist parameter (video in playlist)."""
        url = "https://www.youtube.com/watch?v=abc123&list=PL456"
        assert parse_youtube_playlist_id(url) == "PL456"

    def test_valid_shortened_youtube_url(self) -> None:
        """Test parsing a shortened YouTube URL with playlist parameter."""
        url = "https://youtu.be/abc123?list=PL789"
        assert parse_youtube_playlist_id(url) == "PL789"

    def test_valid_playlist_with_underscore(self) -> None:
        """Test parsing a playlist ID with underscores."""
        url = "https://www.youtube.com/playlist?list=PL_123_ABC"
        assert parse_youtube_playlist_id(url) == "PL_123_ABC"

    def test_valid_playlist_with_dash(self) -> None:
        """Test parsing a playlist ID with dashes."""
        url = "https://www.youtube.com/playlist?list=PL-123-ABC"
        assert parse_youtube_playlist_id(url) == "PL-123-ABC"

    def test_reject_video_only_url(self) -> None:
        """Test rejecting a video-only URL without a list parameter."""
        url = "https://www.youtube.com/watch?v=abc123"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_video_only_shortened_url(self) -> None:
        """Test rejecting a shortened video-only URL without a list parameter."""
        url = "https://youtu.be/abc123"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_playlist_without_list_param(self) -> None:
        """Test rejecting a playlist URL without the list parameter."""
        url = "https://www.youtube.com/playlist"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_empty_list_param(self) -> None:
        """Test rejecting a URL with an empty list parameter."""
        url = "https://www.youtube.com/playlist?list="
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_malformed_url(self) -> None:
        """Test rejecting a malformed URL."""
        url = "not a url"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_other_youtube_paths_without_list(self) -> None:
        """Test rejecting other YouTube paths without a list parameter."""
        urls = [
            "https://www.youtube.com/c/ChannelName",
            "https://www.youtube.com/user/username",
            "https://www.youtube.com/feed/subscriptions",
            "https://www.youtube.com/channel/UC123",
        ]
        for url in urls:
            with pytest.raises(ValueError, match="No playlist ID found in URL"):
                parse_youtube_playlist_id(url)

    @pytest.mark.parametrize(
        "url,expected_id",
        [
            ("https://www.youtube.com/playlist?list=PL123", "PL123"),
            ("https://music.youtube.com/playlist?list=PL456", "PL456"),
            ("https://www.youtube.com/playlist?list=PL789&index=1", "PL789"),
            ("https://www.youtube.com/watch?v=abc&list=PL111", "PL111"),
            ("https://youtu.be/abc?list=PL222", "PL222"),
            ("https://www.youtube.com/playlist?list=PL_ABC_123", "PL_ABC_123"),
            ("https://www.youtube.com/playlist?list=PL-ABC-123", "PL-ABC-123"),
        ],
    )
    def test_various_valid_urls(self, url: str, expected_id: str) -> None:
        """Test various valid YouTube playlist URLs."""
        assert parse_youtube_playlist_id(url) == expected_id


class TestParseYouTubeDurationMs:
    """Tests for parse_youtube_duration_ms function."""

    def test_valid_iso_8601_duration_seconds(self) -> None:
        """Test parsing a valid ISO 8601 duration in seconds."""
        duration_str = "PT10M5S"
        expected_ms = 605000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_minutes(self) -> None:
        """Test parsing a valid ISO 8601 duration in minutes."""
        duration_str = "PT3M30S"
        expected_ms = 210000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_hours(self) -> None:
        """Test parsing a valid ISO 8601 duration in hours."""
        duration_str = "PT1H2M10S"
        expected_ms = 3730000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_zero(self) -> None:
        """Test parsing a zero duration."""
        duration_str = "PT0S"
        expected_ms = 0
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_seconds_only(self) -> None:
        """Test parsing a duration with seconds only."""
        duration_str = "PT45S"
        expected_ms = 45000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_minutes_only(self) -> None:
        """Test parsing a duration with minutes only."""
        duration_str = "PT2M"
        expected_ms = 120000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_hours_only(self) -> None:
        """Test parsing a duration with hours only."""
        duration_str = "PT3H"
        expected_ms = 10800000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_invalid_iso_8601_duration(self) -> None:
        """Test parsing an invalid duration string."""
        duration_str = "invalid"
        assert parse_youtube_duration_ms(duration_str) is None

    def test_none_duration(self) -> None:
        """Test parsing None as duration."""
        assert parse_youtube_duration_ms(None) is None

    def test_incomplete_duration(self) -> None:
        """Test parsing an incomplete duration string."""
        duration_str = "PT"
        assert parse_youtube_duration_ms(duration_str) is None


class TestMapYouTubeError:
    """Tests for map_youtube_error function."""

    def test_map_youtube_error_401_authentication_required(self) -> None:
        """Test mapping HTTP 401 to AuthenticationRequired."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 401
                self.reason = "Unauthorized"

        error = HttpError(MockHttpResponse(), b"Authentication failed")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, AuthenticationRequired)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_403_permission_denied(self) -> None:
        """Test mapping HTTP 403 to PermissionDenied."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 403
                self.reason = "Forbidden"

        error = HttpError(MockHttpResponse(), b"Permission denied")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, PermissionDenied)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_404_provider_not_found(self) -> None:
        """Test mapping HTTP 404 to ProviderNotFound."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 404
                self.reason = "Not Found"

        error = HttpError(MockHttpResponse(), b"Resource not found")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, ProviderNotFound)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_429_rate_limited(self) -> None:
        """Test mapping HTTP 429 to RateLimited."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 429
                self.reason = "Too Many Requests"
                self.headers = {}

        error = HttpError(MockHttpResponse(), b"Rate limit exceeded")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, RateLimited)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_429_preserves_retry_metadata(self) -> None:
        """Test that HTTP 429 mapping preserves Retry-After metadata."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 429
                self.reason = "Too Many Requests"
                self.headers = {"Retry-After": "60"}

        error = HttpError(MockHttpResponse(), b"Rate limit exceeded")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, RateLimited)
        assert result.service == "youtube"
        assert result.operation == operation
        assert "Retry-After" in str(result)
        assert "60" in str(result)

    @pytest.mark.parametrize(
        "status_code,reason",
        [
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
            (505, "HTTP Version Not Supported"),
            (511, "Network Authentication Required"),
        ],
    )
    def test_map_youtube_error_5xx_temporary_provider_failure(self, status_code: int, reason: str) -> None:
        """Test mapping HTTP 5xx status codes to TemporaryProviderFailure."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = status_code
                self.reason = reason

        error = HttpError(MockHttpResponse(), f"{reason} error".encode())
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, TemporaryProviderFailure)
        assert result.service == "youtube"
        assert result.operation == operation
        assert str(status_code) in str(result)

    def test_map_youtube_error_unknown_status_invalid_response(self) -> None:
        """Test mapping an unknown HTTP status to InvalidProviderResponse."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 418
                self.reason = "I'm a teapot"

        error = HttpError(MockHttpResponse(), b"I'm a teapot")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_429_preserves_retry_metadata_with_headers_object(self) -> None:
        """Test that HTTP 429 mapping preserves Retry-After metadata when headers are present as an object."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHeaders:
            def __init__(self):
                self._headers = {"Retry-After": "120"}

            def get(self, key, default=None):
                return self._headers.get(key, default)

        class MockHttpResponse:
            def __init__(self):
                self.status = 429
                self.reason = "Too Many Requests"
                self.headers = MockHeaders()

        error = HttpError(MockHttpResponse(), b"Rate limit exceeded")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, RateLimited)
        assert result.service == "youtube"
        assert result.operation == operation
        assert "Retry-After" in str(result)
        assert "120" in str(result)


class TestFetchYouTubePlaylistMetadata:
    """Tests for fetch_youtube_playlist_metadata function."""

    def test_builds_metadata_from_response(self) -> None:
        """Test that metadata is correctly built from a response."""
        # This is a stub test - implementation will come in later steps
        pass
