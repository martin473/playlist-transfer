"""Scoring functions for matching."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playlist_bridge.domain.models import MatchingConfig


def duration_similarity(
    source_duration_ms: int | None,
    candidate_duration_ms: int,
    config: "MatchingConfig",
) -> float:
    """Return a similarity score between source and candidate durations.

    Returns full credit (1.0) when the difference is at most
    max(duration_full_credit_floor_ms, source_duration_ms * duration_full_credit_ratio).

    Declines linearly to zero at
    max(duration_zero_credit_floor_ms, source_duration_ms * duration_zero_credit_ratio).

    Returns 0.0 when either duration is absent or candidate duration is 0.

    Args:
        source_duration_ms: Source track duration in milliseconds, or None if unknown.
        candidate_duration_ms: Candidate track duration in milliseconds.
        config: MatchingConfig with duration threshold parameters.

    Returns:
        float: Similarity score between 0.0 and 1.0.

    Examples:
        >>> # Assuming config with full_credit_floor_ms=2500, full_credit_ratio=0.02,
        >>> # zero_credit_floor_ms=15000, zero_credit_ratio=0.10
        >>> duration_similarity(120000, 120000, config)
        1.0
        >>> duration_similarity(120000, 123000, config)
        1.0  # within 2% (2400ms) and 2500ms floor
        >>> duration_similarity(120000, 132000, config)
        ~0.5  # halfway between full and zero credit
        >>> duration_similarity(120000, 140000, config)
        0.0  # beyond 10% (12000ms) and 15000ms floor
    """
    # Validate inputs
    if source_duration_ms is None or source_duration_ms <= 0:
        return 0.0
    if candidate_duration_ms <= 0:
        return 0.0

    # Extract config parameters
    full_floor = getattr(config, "duration_full_credit_floor_ms", 2500)
    full_ratio = getattr(config, "duration_full_credit_ratio", 0.02)
    zero_floor = getattr(config, "duration_zero_credit_floor_ms", 15000)
    zero_ratio = getattr(config, "duration_zero_credit_ratio", 0.10)

    # Calculate the difference
    delta = abs(candidate_duration_ms - source_duration_ms)

    # Calculate full credit threshold
    full_threshold = max(full_floor, source_duration_ms * full_ratio)

    # If within full credit threshold, return 1.0
    if delta <= full_threshold:
        return 1.0

    # Calculate zero credit threshold
    zero_threshold = max(zero_floor, source_duration_ms * zero_ratio)

    # If beyond zero credit threshold, return 0.0
    if delta >= zero_threshold:
        return 0.0

    # Linear interpolation between full and zero credit
    # At full_threshold: score = 1.0
    # At zero_threshold: score = 0.0
    score = 1.0 - ((delta - full_threshold) / (zero_threshold - full_threshold))

    # Clamp to [0, 1] for safety
    return max(0.0, min(1.0, score))
