"""Application path helpers for playlist-bridge.

This module provides platform-specific directory paths for configuration,
data, cache, jobs, reports, and database storage. All paths follow the
platform conventions (XDG on Linux, AppData on Windows, Application
Support on macOS) via the platformdirs library.
"""

from pathlib import Path

from platformdirs import user_config_dir, user_data_dir


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
