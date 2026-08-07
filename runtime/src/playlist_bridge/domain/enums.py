"""Domain enums for the playlist bridge."""

from enum import Enum


class SourceService(str, Enum):
    """Supported source services.

    Only YouTube is supported in the initial version.
    """

    YOUTUBE = "youtube"


class DestinationService(str, Enum):
    """Supported destination services.

    Only Spotify is supported in the initial version.
    """

    SPOTIFY = "spotify"
