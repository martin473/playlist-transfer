"""Unit tests for application path helpers."""

from pathlib import Path

from playlist_bridge.paths import config_dir, data_dir


def test_config_dir_returns_path_beneath_platform_config_base() -> None:
    """Test that config_dir returns a path beneath the platform config base."""
    path = config_dir()
    assert isinstance(path, Path)
    # The path should contain "playlist-bridge" as the application name
    assert "playlist-bridge" in str(path)
    # Ensure it's an absolute path
    assert path.is_absolute()


def test_data_dir_returns_path_beneath_platform_data_base() -> None:
    """Test that data_dir returns a path beneath the platform data base."""
    path = data_dir()
    assert isinstance(path, Path)
    # The path should contain "playlist-bridge" as the application name
    assert "playlist-bridge" in str(path)
    # Ensure it's an absolute path
    assert path.is_absolute()
