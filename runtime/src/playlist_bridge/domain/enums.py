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


#: Set of terminal job statuses that represent final states.
#: Terminal statuses are those where no further work can or will be done.
TERMINAL_JOB_STATUSES: frozenset[JobStatus] = frozenset(
    [
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED,
    ]
)


def is_terminal_job_status(status: JobStatus) -> bool:
    """Return True if the job status is terminal (completed, failed, or cancelled).

    Args:
        status: The job status to check.

    Returns:
        bool: True if the status is terminal, False otherwise.
    """
    return status in TERMINAL_JOB_STATUSES


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


class TrackStatus(str, Enum):
    """Track-level states for individual source items.

    States:
        AVAILABLE: Source item is available and can be matched.
        PENDING: Track not yet processed.
        MATCHING: Currently attempting to find a match.
        REVIEW: Match requires manual review.
        ACCEPTED: Match accepted and will be written.
        UNAVAILABLE: Source item is unavailable (deleted/private).
        SKIPPED: Track skipped (e.g., non-song item).
        UNMATCHED: No suitable match found.
        FAILED: Processing failed with an error.
    """

    AVAILABLE = "available"
    PENDING = "pending"
    MATCHING = "matching"
    REVIEW = "review"
    ACCEPTED = "accepted"
    UNAVAILABLE = "unavailable"
    SKIPPED = "skipped"
    UNMATCHED = "unmatched"
    FAILED = "failed"


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
