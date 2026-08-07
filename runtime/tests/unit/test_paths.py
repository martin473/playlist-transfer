"""Unit tests for application path helpers."""

from pathlib import Path

from playlist_bridge.paths import cache_dir, config_dir, data_dir, jobs_dir


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


def test_cache_dir_returns_path_beneath_platform_cache_base() -> None:
    """Test that cache_dir returns a path beneath the platform cache base."""
    path = cache_dir()
    assert isinstance(path, Path)
    # The path should contain "playlist-bridge" as the application name
    assert "playlist-bridge" in str(path)
    # Ensure it's an absolute path
    assert path.is_absolute()


def test_jobs_dir_returns_path_beneath_data_dir() -> None:
    """Test that jobs_dir returns a path beneath data_dir()."""
    path = jobs_dir()
    assert isinstance(path, Path)
    # The path should be beneath data_dir()
    assert str(path).startswith(str(data_dir()))
    # The path should contain "jobs" as the final component
    assert path.name == "jobs"
    # Ensure it's an absolute path
    assert path.is_absolute()
