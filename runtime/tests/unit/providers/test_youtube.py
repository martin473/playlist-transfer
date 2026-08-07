"""Unit tests for YouTube provider utilities."""

import pytest

from playlist_bridge.providers.youtube import parse_youtube_duration_ms


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
