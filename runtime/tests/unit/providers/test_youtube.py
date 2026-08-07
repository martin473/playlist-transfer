"""Unit tests for YouTube provider utilities."""

import pytest

from playlist_bridge.providers.youtube import (
    parse_youtube_duration_ms,
    parse_youtube_playlist_id,
)


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
            ("https://www.youtube.com/playlist?list=PL123&index=2&t=30", "PL123"),
        ],
    )
    def test_parametrized_valid_urls(self, url: str, expected_id: str) -> None:
        """Test multiple valid playlist URLs with parametrization."""
        assert parse_youtube_playlist_id(url) == expected_id

    @pytest.mark.parametrize(
        "invalid_url",
        [
            "https://www.youtube.com/watch?v=abc123",
            "https://youtu.be/abc123",
            "https://www.youtube.com/playlist",
            "https://www.youtube.com/playlist?list=",
            "https://music.youtube.com/playlist?list=",
            "not a url",
            "https://www.youtube.com/c/ChannelName",
            "https://www.youtube.com/channel/UC123",
            "https://www.youtube.com/watch?",
            "https://www.youtube.com/",
        ],
    )
    def test_parametrized_invalid_urls(self, invalid_url: str) -> None:
        """Test multiple invalid URLs raise ValueError."""
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(invalid_url)

    def test_strips_whitespace_from_url(self) -> None:
        """Test that whitespace is stripped from the URL."""
        url = "  https://www.youtube.com/playlist?list=PL123  "
        assert parse_youtube_playlist_id(url) == "PL123"


class TestParseYouTubeDurationMs:
    """Tests for parse_youtube_duration_ms function."""

    def test_parse_seconds(self) -> None:
        """Test parsing durations with only seconds."""
        assert parse_youtube_duration_ms("PT5S") == 5000
        assert parse_youtube_duration_ms("PT30S") == 30000
        assert parse_youtube_duration_ms("PT0S") == 0

    def test_parse_minutes(self) -> None:
        """Test parsing durations with minutes."""
        assert parse_youtube_duration_ms("PT1M") == 60000
        assert parse_youtube_duration_ms("PT1M30S") == 90000
        assert parse_youtube_duration_ms("PT5M") == 300000
        assert parse_youtube_duration_ms("PT10M") == 600000

    def test_parse_hours(self) -> None:
        """Test parsing durations with hours."""
        assert parse_youtube_duration_ms("PT1H") == 3600000
        assert parse_youtube_duration_ms("PT1H2M3S") == 3723000
        assert parse_youtube_duration_ms("PT2H30M") == 9000000
        assert parse_youtube_duration_ms("PT10H") == 36000000

    def test_parse_complex_durations(self) -> None:
        """Test parsing durations with various combinations."""
        assert parse_youtube_duration_ms("PT1H30M45S") == 5445000
        assert parse_youtube_duration_ms("PT1M5S") == 65000
        assert parse_youtube_duration_ms("PT2H5S") == 7205000
        # YouTube live streams often have no duration
        assert parse_youtube_duration_ms("P0D") == 0

    def test_none_and_empty_inputs(self) -> None:
        """Test that None and empty inputs return None."""
        assert parse_youtube_duration_ms(None) is None
        assert parse_youtube_duration_ms("") is None
        assert parse_youtube_duration_ms("   ") is None
        assert parse_youtube_duration_ms("\n") is None
        assert parse_youtube_duration_ms("\t") is None

    def test_malformed_values(self) -> None:
        """Test that malformed duration strings return None."""
        assert parse_youtube_duration_ms("invalid") is None
        assert parse_youtube_duration_ms("PT") is None
        assert parse_youtube_duration_ms("P1D") is None  # Days not used for video durations
        assert parse_youtube_duration_ms("PT1M60S") is None  # Invalid seconds
        assert parse_youtube_duration_ms("random text") is None

    def test_live_streams(self) -> None:
        """Test handling of live stream durations."""
        # Live streams often have zero duration or are missing
        assert parse_youtube_duration_ms("P0D") == 0
        assert parse_youtube_duration_ms("PT0H0M0S") == 0
        # Some live streams may have a duration once ended
        assert parse_youtube_duration_ms("PT2H") == 7200000

    def test_negative_durations(self) -> None:
        """Test that negative durations return None."""
        # YouTube videos cannot have negative duration, but test defensive handling
        assert parse_youtube_duration_ms("PT-1M") is None
        assert parse_youtube_duration_ms("-PT1M") is None

    def test_edge_cases(self) -> None:
        """Test various edge cases."""
        # Very long durations (should handle large numbers)
        assert parse_youtube_duration_ms("PT100H") == 360000000
        assert parse_youtube_duration_ms("PT1000M") == 60000000
        # Fractional seconds (ISO 8601 allows this, but YouTube durations rarely have them)
        assert parse_youtube_duration_ms("PT1.5S") == 1500
        # Leading/trailing whitespace should be stripped
        assert parse_youtube_duration_ms("  PT1M  ") == 60000

    @pytest.mark.parametrize(
        "duration_str,expected_ms",
        [
            ("PT1S", 1000),
            ("PT15S", 15000),
            ("PT1M", 60000),
            ("PT2M", 120000),
            ("PT1H", 3600000),
            ("PT3H", 10800000),
            ("PT1M1S", 61000),
            ("PT1H1M1S", 3661000),
        ],
    )
    def test_parametrized_valid_durations(
        self, duration_str: str, expected_ms: int
    ) -> None:
        """Test multiple valid duration strings with parametrization."""
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    @pytest.mark.parametrize(
        "invalid_input",
        [
            None,
            "",
            "   ",
            "invalid",
            "P1D",
            "PT1M60S",
            "PT1H60M",
            "random text",
            "PT",
            "P",
            "PT-1M",
        ],
    )
    def test_parametrized_invalid_inputs(self, invalid_input: str) -> None:
        """Test multiple invalid inputs return None."""
        assert parse_youtube_duration_ms(invalid_input) is None
