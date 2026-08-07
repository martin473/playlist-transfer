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


class MatchPolicy(str, Enum):
    """Match policy controlling how aggressively matches are accepted.

    Values:
        STRICT: Only accept high-confidence matches.
        BALANCED: Balance precision and recall.
        LOOSE: Accept lower-confidence matches to maximize coverage.
    """

    STRICT = "strict"
    BALANCED = "balanced"
    LOOSE = "loose"


class TransferMode(str, Enum):
    """Transfer mode controlling destination playlist mutation.

    Values:
        DRY_RUN: Simulate transfer without writing changes.
        CREATE: Create a new destination playlist.
        MERGE: Merge tracks into an existing playlist.
        REPLACE: Replace the entire destination playlist contents.
    """

    DRY_RUN = "dry_run"
    CREATE = "create"
    MERGE = "merge"
    REPLACE = "replace"
