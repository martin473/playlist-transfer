"""Unit tests for application path helpers."""

from pathlib import Path

from playlist_bridge.paths import cache_dir, config_dir, data_dir, jobs_dir, reports_dir, database_path, ensure_app_directories


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


def test_reports_dir_returns_path_beneath_data_dir() -> None:
    """Test that reports_dir returns a path beneath data_dir()."""
    path = reports_dir()
    assert isinstance(path, Path)
    # The path should be beneath data_dir()
    assert str(path).startswith(str(data_dir()))
    # The path should contain "reports" as the final component
    assert path.name == "reports"
    # Ensure it's an absolute path
    assert path.is_absolute()


def test_database_path_returns_path_beneath_data_dir() -> None:
    """Test that database_path returns a path beneath data_dir()."""
    path = database_path()
    assert isinstance(path, Path)
    # The path should be beneath data_dir()
    assert str(path).startswith(str(data_dir()))
    # The path should have the expected filename
    assert path.name == "playlist_bridge.db"
    # Ensure it's an absolute path
    assert path.is_absolute()


def test_ensure_app_directories_creates_required_directories() -> None:
    """Test that ensure_app_directories creates all required directories.

    This test verifies that calling ensure_app_directories() twice succeeds
    and leaves all required directories present.
    """
    import tempfile
    from pathlib import Path
    from unittest.mock import patch

    with patch("playlist_bridge.paths.config_dir") as mock_config, \
         patch("playlist_bridge.paths.data_dir") as mock_data, \
         patch("playlist_bridge.paths.cache_dir") as mock_cache:

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            config_path = tmp_path / "config"
            data_path = tmp_path / "data"
            cache_path = tmp_path / "cache"

            mock_config.return_value = config_path
            mock_data.return_value = data_path
            mock_cache.return_value = cache_path

            # First call should create all directories
            ensure_app_directories()

            # Verify all directories exist
            assert config_path.exists() and config_path.is_dir()
            assert data_path.exists() and data_path.is_dir()
            assert cache_path.exists() and cache_path.is_dir()
            assert (data_path / "jobs").exists() and (data_path / "jobs").is_dir()
            assert (data_path / "reports").exists() and (data_path / "reports").is_dir()

            # Second call should succeed without errors
            ensure_app_directories()

            # Verify directories still exist
            assert config_path.exists() and config_path.is_dir()
            assert data_path.exists() and data_path.is_dir()
            assert cache_path.exists() and cache_path.is_dir()
            assert (data_path / "jobs").exists() and (data_path / "jobs").is_dir()
            assert (data_path / "reports").exists() and (data_path / "reports").is_dir()
