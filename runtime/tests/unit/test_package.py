"""Tests for the package initializer."""

import playlist_bridge


def test_version_is_non_empty_string() -> None:
    """Test that importing playlist_bridge returns a non-empty version string."""
    assert isinstance(playlist_bridge.__version__, str)
    assert playlist_bridge.__version__
