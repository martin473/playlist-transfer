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


class JobStatus(str, Enum):
    """Lifecycle states for a transfer job.

    States:
        PENDING: Job created but not yet started.
        READING: Reading source playlist items.
        MATCHING: Matching source items to destination candidates.
        REVIEW: Matches require manual review.
        WRITING: Writing matched tracks to destination playlist.
        VERIFYING: Verifying destination playlist contents.
        COMPLETED: Job finished successfully.
        FAILED: Job terminated with an error.
        CANCELLED: Job cancelled by user or system.
    """

    PENDING = "pending"
    READING = "reading"
    MATCHING = "matching"
    REVIEW = "review"
    WRITING = "writing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
