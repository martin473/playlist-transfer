"""Unit tests for scoring functions."""

import pytest

from playlist_bridge.matching.scoring import duration_similarity


class _TestMatchingConfig:
    """Minimal config class for testing duration_similarity.

    This matches the fields that duration_similarity expects from MatchingConfig.
    The real MatchingConfig will be defined in domain/models.py.
    """

    def __init__(
        self,
        duration_full_credit_floor_ms: int = 2500,
        duration_full_credit_ratio: float = 0.02,
        duration_zero_credit_floor_ms: int = 15000,
        duration_zero_credit_ratio: float = 0.10,
    ):
        self.duration_full_credit_floor_ms = duration_full_credit_floor_ms
        self.duration_full_credit_ratio = duration_full_credit_ratio
        self.duration_zero_credit_floor_ms = duration_zero_credit_floor_ms
        self.duration_zero_credit_ratio = duration_zero_credit_ratio


@pytest.fixture
def default_config():
    """Return a default config for testing."""
    return _TestMatchingConfig()


class TestDurationSimilarity:
    """Tests for duration_similarity function."""

    def test_exact_match(self, default_config):
        """Test exact duration match returns 1.0."""
        result = duration_similarity(120000, 120000, default_config)
        assert result == 1.0

    def test_very_close_within_floor(self, default_config):
        """Test that differences within full_credit_floor_ms return 1.0."""
        # 2.0 seconds difference, less than 2500ms floor
        result = duration_similarity(120000, 122000, default_config)
        assert result == 1.0

    def test_close_within_ratio(self, default_config):
        """Test that differences within 2% ratio return 1.0."""
        # 2400ms difference, exactly 2% of 120000ms
        result = duration_similarity(120000, 122400, default_config)
        assert result == 1.0

    def test_beyond_full_but_below_zero(self, default_config):
        """Test linear decline between full and zero credit thresholds."""
        # 6.0 seconds difference, between full (2500ms) and zero (15000ms)
        # At delta=6000, score should be approximately 0.72
        result = duration_similarity(120000, 126000, default_config)
        # delta=6000, full_threshold=2500, zero_threshold=15000
        # score = 1.0 - (6000-2500)/(15000-2500) = 1.0 - 3500/12500 = 1.0 - 0.28 = 0.72
        assert result == 0.72

    def test_at_zero_credit_threshold(self, default_config):
        """Test that at zero credit threshold returns 0.0."""
        # delta=15000ms (zero_threshold = max(15000, 12000) = 15000)
        result = duration_similarity(120000, 135000, default_config)
        assert result == 0.0

    def test_beyond_zero_credit(self, default_config):
        """Test that beyond zero credit threshold returns 0.0."""
        result = duration_similarity(120000, 140000, default_config)
        assert result == 0.0

    def test_short_duration_with_floor(self, default_config):
        """Test that floor applies for short durations."""
        # For 10-second track, 2% is 200ms, but floor is 2500ms
        # So full credit up to 2500ms difference
        result = duration_similarity(10000, 12500, default_config)
        assert result == 1.0  # 2500ms <= floor

        # At 2600ms, just beyond floor, but within zero floor (15000ms)
        # delta=2600, full_threshold=2500, zero_threshold=15000 (max(15000, 1000))
        # score = 1.0 - (2600-2500)/(15000-2500) = 1.0 - 100/12500 = 0.992
        result = duration_similarity(10000, 12600, default_config)
        assert result == 0.992

    def test_very_short_duration(self, default_config):
        """Test for very short durations where zero floor dominates."""
        # For 5-second track, 10% is 500ms, but zero_floor is 15000ms
        # So zero credit only at 15000ms difference
        result = duration_similarity(5000, 20000, default_config)
        # delta=15000, full_threshold=2500, zero_threshold=15000
        # score = 1.0 - (15000-2500)/(15000-2500) = 0.0
        assert result == 0.0

        result = duration_similarity(5000, 17500, default_config)
        # delta=12500, full_threshold=2500, zero_threshold=15000
        # score = 1.0 - (12500-2500)/(15000-2500) = 1.0 - 10000/12500 = 0.2
        assert result == pytest.approx(0.2)

    def test_source_duration_none(self, default_config):
        """Test that None source duration returns 0.0."""
        result = duration_similarity(None, 120000, default_config)
        assert result == 0.0

    def test_source_duration_zero(self, default_config):
        """Test that zero source duration returns 0.0."""
        result = duration_similarity(0, 120000, default_config)
        assert result == 0.0

    def test_candidate_duration_zero(self, default_config):
        """Test that zero candidate duration returns 0.0."""
        result = duration_similarity(120000, 0, default_config)
        assert result == 0.0

    def test_both_durations_zero(self, default_config):
        """Test that both durations zero returns 0.0."""
        result = duration_similarity(0, 0, default_config)
        assert result == 0.0

    def test_source_duration_missing_candidate_zero(self, default_config):
        """Test missing source and zero candidate returns 0.0."""
        result = duration_similarity(None, 0, default_config)
        assert result == 0.0

    def test_large_duration_small_delta(self, default_config):
        """Test large duration with very small difference."""
        # 10-minute song with 1-second difference
        result = duration_similarity(600000, 601000, default_config)
        # delta=1000, full_threshold=max(2500, 12000)=12000
        # 1000 <= 12000, so full credit
        assert result == 1.0

    def test_large_duration_medium_delta(self, default_config):
        """Test large duration with medium difference."""
        # 10-minute song with 30-second difference (5%)
        result = duration_similarity(600000, 630000, default_config)
        # delta=30000, full_threshold=12000, zero_threshold=60000
        # score = 1.0 - (30000-12000)/(60000-12000) = 1.0 - 18000/48000 = 0.625
        assert result == 0.625

    def test_large_duration_large_delta(self, default_config):
        """Test large duration with large difference."""
        # 10-minute song with 60-second difference (10%)
        result = duration_similarity(600000, 660000, default_config)
        # delta=60000, zero_threshold=60000, so 0.0
        assert result == 0.0

    def test_custom_thresholds(self):
        """Test with custom config thresholds."""
        config = _TestMatchingConfig(
            duration_full_credit_floor_ms=5000,
            duration_full_credit_ratio=0.05,
            duration_zero_credit_floor_ms=30000,
            duration_zero_credit_ratio=0.20,
        )

        # For 120000ms source:
        # full_threshold = max(5000, 6000) = 6000
        # zero_threshold = max(30000, 24000) = 30000
        result = duration_similarity(120000, 126000, config)
        # delta=6000, exactly at full threshold
        assert result == 1.0

        result = duration_similarity(120000, 132000, config)
        # delta=12000, between 6000 and 30000
        # score = 1.0 - (12000-6000)/(30000-6000) = 1.0 - 6000/24000 = 0.75
        assert result == 0.75

        result = duration_similarity(120000, 150000, config)
        # delta=30000, exactly at zero threshold
        assert result == 0.0

    def test_custom_thresholds_short_duration(self):
        """Test custom thresholds with short duration."""
        config = _TestMatchingConfig(
            duration_full_credit_floor_ms=5000,
            duration_full_credit_ratio=0.05,
            duration_zero_credit_floor_ms=30000,
            duration_zero_credit_ratio=0.20,
        )

        # For 10000ms source:
        # full_threshold = max(5000, 500) = 5000
        # zero_threshold = max(30000, 2000) = 30000
        result = duration_similarity(10000, 15000, config)
        # delta=5000, exactly at full threshold
        assert result == 1.0

        result = duration_similarity(10000, 20000, config)
        # delta=10000, between 5000 and 30000
        # score = 1.0 - (10000-5000)/(30000-5000) = 1.0 - 5000/25000 = 0.8
        assert result == 0.8

    def test_edge_cases(self, default_config):
        """Test edge cases."""
        # Very large duration with small difference
        result = duration_similarity(3600000, 3600001, default_config)  # 1 hour + 1ms
        assert result == 1.0

        # Very large duration with significant difference (2.5%)
        # delta=90000, full_threshold=max(2500, 72000)=72000, zero_threshold=max(15000, 360000)=360000
        result = duration_similarity(3600000, 3690000, default_config)
        # score = 1.0 - (90000-72000)/(360000-72000) = 1.0 - 18000/288000 = 0.9375
        assert result == 0.9375

    def test_boundary_values(self, default_config):
        """Test boundary values for precision."""
        # Just below full threshold (full_threshold=2500)
        result = duration_similarity(120000, 122499, default_config)
        assert result == 1.0  # 2499ms < 2500ms threshold

        # Just above full threshold
        result = duration_similarity(120000, 122501, default_config)
        # delta=2501, full_threshold=2500, zero_threshold=15000
        # score = 1.0 - (2501-2500)/(15000-2500) = 1.0 - 1/12500 = 0.99992
        # Using pytest.approx for floating point comparison
        assert result == pytest.approx(0.99992, abs=1e-6)

        # Just below zero threshold
        result = duration_similarity(120000, 134999, default_config)
        # delta=14999, zero_threshold=15000
        # score = 1.0 - (14999-2500)/(15000-2500) = 1.0 - 12499/12500 = 0.00008
        assert result == pytest.approx(0.00008, abs=1e-6)

        # Just above zero threshold
        result = duration_similarity(120000, 135001, default_config)
        # delta=15001 > zero_threshold=15000
        assert result == 0.0

    def test_negative_durations(self, default_config):
        """Test that negative durations are treated as invalid."""
        result = duration_similarity(-100, 120000, default_config)
        assert result == 0.0

        result = duration_similarity(120000, -100, default_config)
        assert result == 0.0

        result = duration_similarity(-100, -100, default_config)
        assert result == 0.0
