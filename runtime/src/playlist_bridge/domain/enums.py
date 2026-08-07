"""Domain enums for the playlist bridge."""

from enum import Enum


class SourceService(str, Enum):
    """Supported source services.

    Only YouTube is supported in the initial version.
    """

    YOUTUBE = "youtube"
