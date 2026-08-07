"""Unit tests for job ID generation and validation."""

import pytest

from playlist_bridge.jobs.runner import new_job_id, validate_job_id


class TestNewJobId:
    """Tests for the new_job_id function."""

    def test_returns_string(self) -> None:
        """new_job_id should return a string."""
        job_id = new_job_id()
        assert isinstance(job_id, str)

    def test_returns_hex_string(self) -> None:
        """new_job_id should return a valid hex string."""
        job_id = new_job_id()
        assert len(job_id) == 32
        assert all(c.isalnum() for c in job_id)

    def test_returns_different_ids(self) -> None:
        """new_job_id should generate different IDs each call."""
        job_id1 = new_job_id()
        job_id2 = new_job_id()
        job_id3 = new_job_id()
        assert job_id1 != job_id2
        assert job_id1 != job_id3
        assert job_id2 != job_id3

    def test_returns_filename_safe(self) -> None:
        """new_job_id should return strings safe for filenames."""
        job_id = new_job_id()
        # UUID hex characters are safe in filenames
        assert all(c.isalnum() for c in job_id)
        assert " " not in job_id
        assert "/" not in job_id
        assert "\\" not in job_id

    def test_unique_across_large_sample(self) -> None:
        """Generated IDs should be unique across a large sample."""
        sample_size = 10_000
        job_ids = {new_job_id() for _ in range(sample_size)}
        assert len(job_ids) == sample_size


class TestValidateJobId:
    """Tests for the validate_job_id function."""

    def test_returns_true_for_valid_id(self) -> None:
        """validate_job_id should return True for a valid job ID."""
        job_id = new_job_id()
        assert validate_job_id(job_id) is True

    def test_returns_true_for_known_hex_string(self) -> None:
        """validate_job_id should return True for a known 32-char hex string."""
        job_id = "1234567890abcdef1234567890abcdef"
        assert validate_job_id(job_id) is True

    def test_returns_false_for_none(self) -> None:
        """validate_job_id should return False for None."""
        assert validate_job_id(None) is False

    def test_returns_false_for_empty_string(self) -> None:
        """validate_job_id should return False for empty string."""
        assert validate_job_id("") is False

    def test_returns_false_for_short_string(self) -> None:
        """validate_job_id should return False for strings shorter than 32 chars."""
        assert validate_job_id("abc123") is False

    def test_returns_false_for_long_string(self) -> None:
        """validate_job_id should return False for strings longer than 32 chars."""
        assert validate_job_id("abc" * 20) is False

    def test_returns_false_for_non_hex_characters(self) -> None:
        """validate_job_id should return False for non-hex characters."""
        assert validate_job_id("g" * 32) is False
        assert validate_job_id("-" * 32) is False
        assert validate_job_id("_" * 32) is False

    def test_returns_false_for_mixed_valid_invalid(self) -> None:
        """validate_job_id should return False for mixed valid/invalid chars."""
        job_id = "1234567890abcdef1234567890abcde!"
        assert validate_job_id(job_id) is False

    def test_returns_false_for_uppercase_valid(self) -> None:
        """validate_job_id should return True for uppercase hex strings too."""
        job_id = "1234567890ABCDEF1234567890ABCDEF"
        assert validate_job_id(job_id) is True

    def test_returns_false_for_non_string_types(self) -> None:
        """validate_job_id should return False for non-string types."""
        assert validate_job_id(123) is False  # type: ignore
        assert validate_job_id([]) is False  # type: ignore
        assert validate_job_id({}) is False  # type: ignore
        assert validate_job_id(True) is False  # type: ignore
