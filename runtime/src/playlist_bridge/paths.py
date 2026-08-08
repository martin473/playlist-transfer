"""Application path helpers for playlist-bridge.

This module provides platform-specific directory paths for configuration,
data, cache, jobs, reports, and database storage. All paths follow the
platform conventions (XDG on Linux, AppData on Windows, Application
Support on macOS) via the platformdirs library.
"""

from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir


def config_dir() -> Path:
    """Return the platform-specific configuration directory for playlist-bridge.

    Returns:
        Path: The config directory path (e.g., ~/.config/playlist-bridge on Linux,
              ~/Library/Application Support/playlist-bridge on macOS,
              %APPDATA%/playlist-bridge on Windows).

    Side Effects:
        platform_directory_lookup: Resolves the platform-specific config directory.

    Errors:
        None: This function does not raise exceptions under normal conditions.
    """
    return Path(user_config_dir("playlist-bridge", roaming=True))


def data_dir() -> Path:
    """Return the platform-specific data directory for playlist-bridge.

    Returns:
        Path: The data directory path (e.g., ~/.local/share/playlist-bridge on Linux,
              ~/Library/Application Support/playlist-bridge on macOS,
              %APPDATA%/playlist-bridge on Windows).

    Side Effects:
        platform_directory_lookup: Resolves the platform-specific data directory.

    Errors:
        None: This function does not raise exceptions under normal conditions.
    """
    return Path(user_data_dir("playlist-bridge", roaming=True))


def cache_dir() -> Path:
    """Return the platform-specific cache directory for playlist-bridge.

    Returns:
        Path: The cache directory path (e.g., ~/.cache/playlist-bridge on Linux,
              ~/Library/Caches/playlist-bridge on macOS,
              %LOCALAPPDATA%/playlist-bridge/Cache on Windows).

    Side Effects:
        platform_directory_lookup: Resolves the platform-specific cache directory.

    Errors:
        None: This function does not raise exceptions under normal conditions.
    """
    return Path(user_cache_dir("playlist-bridge"))


def jobs_dir() -> Path:
    """Return the jobs directory beneath the application data directory.

    Returns:
        Path: The jobs directory path beneath data_dir().

    Side Effects:
        platform_directory_lookup: Resolves the platform-specific data directory.

    Errors:
        None: This function does not raise exceptions under normal conditions.
    """
    return data_dir() / "jobs"


def reports_dir() -> Path:
    """Return the reports directory beneath the application data directory.

    Returns:
        Path: The reports directory path beneath data_dir().

    Side Effects:
        platform_directory_lookup: Resolves the platform-specific data directory.

    Errors:
        None: This function does not raise exceptions under normal conditions.
    """
    return data_dir() / "reports"


def database_path() -> Path:
    """Return the SQLite database file path beneath the application data directory.

    Returns:
        Path: The database file path beneath data_dir().

    Side Effects:
        platform_directory_lookup: Resolves the platform-specific data directory.

    Errors:
        None: This function does not raise exceptions under normal conditions.
    """
    return data_dir() / "playlist_bridge.db"


def ensure_app_directories() -> None:
    """Create all application directories required by playlist-bridge.

    This function creates the directories returned by config_dir(), data_dir(),
    cache_dir(), jobs_dir(), and reports_dir(). It does not create the database
    file itself.

    Side Effects:
        filesystem_create_directory: Creates directories on the filesystem.

    Errors:
        OSError: If directory creation fails due to permission or filesystem issues.
    """
    dirs = [config_dir(), data_dir(), cache_dir(), jobs_dir(), reports_dir()]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
