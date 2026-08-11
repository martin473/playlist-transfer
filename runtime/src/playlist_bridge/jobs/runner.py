"""Job runner and job creation for playlist-bridge."""

import json
import uuid
from datetime import datetime, timezone
from typing import NamedTuple, Protocol, Sequence, TextIO, Union, Optional

from playlist_bridge.domain.models import (
    TransferRequest,
    LoadedSourcePlaylist,
    SourcePlaylistMetadata,
    PlaylistReference,
    SourceTrack,
    MatchDecision,
    SpotifyCandidate,
)
from playlist_bridge.ports import JobRepository, JobNotFoundError, LeaseLostError
from playlist_bridge.domain.events import JobEvent, JobEventAdapter, SourceProgressEvent
from playlist_bridge.domain.enums import JobStatus
from playlist_bridge.providers.youtube import SourceAdapter, CancellationToken
from playlist_bridge.jobs.cancellation import EventEmitter


def new_job_id() -> str:
    """Generate a new unique job ID.

    Returns:
        A string containing a UUID4 hex representation safe for use in filenames
        and filesystem paths.

    Examples:
        >>> job_id = new_job_id()
        >>> isinstance(job_id, str)
        True
        >>> len(job_id) == 32
        True
        >>> all(c.isalnum() for c in job_id)
        True
    """
    return uuid.uuid4().hex


def validate_job_id(job_id: Union[str, None]) -> bool:
    """Validate that a job ID is a properly formed UUID4 hex string.

    Args:
        job_id: The job ID string to validate, or None.

    Returns:
        True if the job ID is a 32-character hex string, False otherwise.

    Examples:
        >>> validate_job_id(new_job_id())
        True
        >>> validate_job_id("invalid")
        False
        >>> validate_job_id(None)
        False
        >>> validate_job_id("1234567890abcdef1234567890abcdef")
        True
    """
    if not job_id or not isinstance(job_id, str):
        return False
    if len(job_id) != 32:
        return False
    try:
        int(job_id, 16)
        return True
    except ValueError:
        return False


def create_transfer_job(
    request: TransferRequest,
    jobs: JobRepository,
    now: datetime,
) -> str:
    """Create and persist a transfer job in the pending state.

    This function creates a new job record from a transfer request and persists
    it using the provided JobRepository. The job is created in the "pending"
    state before any provider calls are made.

    Args:
        request: The transfer request containing source/destination details.
        jobs: The JobRepository implementation for persistence.
        now: The current timestamp (timezone-aware) for job creation.

    Returns:
        The job_id of the newly created job (as a hex string).

    Raises:
        ValueError: If the request is invalid.
        IntegrityError: If a job with the generated ID already exists.

    Examples:
        >>> from datetime import datetime, timezone
        >>> from playlist_bridge.domain.models import TransferRequest
        >>> from playlist_bridge.domain.enums import TransferMode
        >>> request = TransferRequest(
        ...     source_service="youtube",
        ...     source_playlist_id="PLabc123",
        ...     destination_service="spotify",
        ...     transfer_mode=TransferMode.CREATE,
        ...     destination_name="My Playlist",
        ... )
        >>> job_id = create_transfer_job(request, jobs, datetime.now(timezone.utc))
        >>> isinstance(job_id, str)
        True
        >>> len(job_id) == 32
        True
    """
    # Generate a new job ID
    job_id = new_job_id()

    # Persist the job using the repository
    job_record = jobs.create(request, job_id, now)

    # Return the job ID
    return job_record.id


class JsonlEventEmitter:
    """Emit JSONL events to a text stream, one event per line.

    This class serializes JobEvent instances to JSON and writes them to the
    provided stream, flushing after each event to ensure immediate delivery.

    Args:
        stream: TextIO stream to write events to (e.g., sys.stdout).

    Raises:
        OSError: If writing to the stream fails.
    """

    def __init__(self, stream: TextIO) -> None:
        """Initialize the emitter with a text stream."""
        self._stream = stream

    def emit(self, event: JobEvent) -> None:
        """Serialize and write a single event to the stream as JSONL.

        Args:
            event: The JobEvent instance to emit.

        Raises:
            OSError: If writing to the stream fails.
        """
        try:
            # Use the JobEventAdapter to ensure proper serialization
            json_data = JobEventAdapter.dump_json(event, by_alias=False)
            self._stream.write(json_data.decode("utf-8") + "\n")
            self._stream.flush()
        except (OSError, ValueError) as e:
            raise OSError(f"Failed to emit JSONL event: {e}") from e


class TransferCounts(NamedTuple):
    """Counts of transfer decisions."""
    matched: int
    ambiguous: int
    unmatched: int
    unavailable: int
    skipped: int
    non_track: int


def calculate_transfer_counts(
    tracks: Sequence[SourceTrack],
    decisions: Sequence[MatchDecision],
) -> TransferCounts:
    """Calculate counts of matched, unmatched, unavailable, and skipped items.

    This function counts source tracks by their match status and availability status,
    returning a TransferCounts tuple. Matched tracks are those with status "matched"
    and a selected_candidate. Unmatched tracks are those with status "unmatched" or
    no decision. Unavailable tracks are counted separately regardless of decisions.

    Args:
        tracks: Sequence of SourceTrack objects in source playlist order.
        decisions: Sequence of MatchDecision objects for the tracks.

    Returns:
        TransferCounts tuple with counts for each category.

    Raises:
        ValueError: If tracks or decisions are invalid.

    Examples:
        >>> from playlist_bridge.domain.models import MatchScore, SpotifyCandidate, SourceTrack, MatchDecision
        >>> track1 = SourceTrack(
        ...     position=0,
        ...     title="Song 1",
        ...     artist_names=["Artist 1"],
        ...     duration_seconds=180,
        ...     video_id="abc123",
        ...     availability="available",
        ... )
        >>> candidate1 = SpotifyCandidate(
        ...     track_id="xyz789",
        ...     uri="spotify:track:xyz789",
        ...     title="Song 1",
        ...     artist_names=["Artist 1"],
        ...     album="Album 1",
        ...     duration_seconds=180,
        ...     explicit=False,
        ... )
        >>> score1 = MatchScore(
        ...     title_similarity=0.95,
        ...     artist_similarity=0.9,
        ...     duration_similarity=1.0,
        ...     version_agreement=1.0,
        ...     unwanted_version_penalty=0.0,
        ...     explicit_state=1.0,
        ...     total_score=0.95,
        ...     reasons=["Good match"],
        ... )
        >>> decision1 = MatchDecision(
        ...     source_item_id="abc123",
        ...     status="matched",
        ...     selected_candidate=candidate1,
        ...     match_score=score1,
        ... )
        >>> track2 = SourceTrack(
        ...     position=1,
        ...     title="Song 2",
        ...     artist_names=["Artist 2"],
        ...     duration_seconds=200,
        ...     video_id="def456",
        ...     availability="available",
        ... )
        >>> decision2 = MatchDecision(
        ...     source_item_id="def456",
        ...     status="unmatched",
        ...     selected_candidate=None,
        ...     match_score=None,
        ... )
        >>> counts = calculate_transfer_counts([track1, track2], [decision1, decision2])
        >>> counts.matched
        1
        >>> counts.unmatched
        1
    """
    if not tracks and not decisions:
        return TransferCounts(0, 0, 0, 0, 0, 0)

    # Build lookup from source_item_id to decision
    decision_lookup: dict[str, MatchDecision] = {}
    for decision in decisions:
        if decision.source_item_id in decision_lookup:
            # Duplicate decisions for same source item - keep the first one
            continue
        decision_lookup[decision.source_item_id] = decision

    matched = 0
    ambiguous = 0
    unmatched = 0
    unavailable = 0
    skipped = 0
    non_track = 0

    for track in tracks:
        # Use video_id as the source_item_id
        source_id = track.video_id
        decision = decision_lookup.get(source_id)

        # Check availability
        avail = track.availability
        if hasattr(avail, "value"):
            avail = avail.value

        if avail == "unavailable":
            unavailable += 1
            continue

        if decision is None:
            unmatched += 1
            continue

        # Count by decision status
        if decision.status == "matched" and decision.selected_candidate is not None:
            matched += 1
        elif decision.status == "ambiguous":
            ambiguous += 1
        elif decision.status == "unmatched":
            unmatched += 1
        elif decision.status == "skipped":
            skipped += 1
        elif decision.status == "non_track":
            non_track += 1
        else:
            # Fallback: treat as unmatched
            unmatched += 1

    return TransferCounts(
        matched=matched,
        ambiguous=ambiguous,
        unmatched=unmatched,
        unavailable=unavailable,
        skipped=skipped,
        non_track=non_track,
    )


# Define RuntimeDependencies as a protocol for dependency injection
class RuntimeDependencies(Protocol):
    """Container for runtime dependencies needed by job stages."""
    jobs: JobRepository
    source_adapter: SourceAdapter


def load_source_stage(
    job_id: str,
    request: TransferRequest,
    dependencies: RuntimeDependencies,
    emit: EventEmitter,
    cancel: CancellationToken,
    lease_token: str,
) -> LoadedSourcePlaylist:
    """Load source playlist for a transfer job.

    This function:
    1. Retrieves the job from the repository
    2. Verifies the lease token
    3. Updates job state to "reading"
    4. Emits a SourceProgressEvent
    5. Loads the playlist using the source adapter
    6. Returns the loaded playlist

    Args:
        job_id: Unique identifier of the job.
        request: Transfer request containing source/destination details.
        dependencies: Runtime dependencies (job repo, source adapter).
        emit: Event emitter callback for job events.
        cancel: Cancellation token for checking if operation should stop.
        lease_token: Lease token for verifying lease ownership.

    Returns:
        LoadedSourcePlaylist containing playlist metadata and ordered tracks.

    Raises:
        JobNotFoundError: If the job does not exist.
        LeaseLostError: If the lease token does not match.
        AuthenticationRequired: If authentication with source service fails.
        PermissionDenied: If access to the playlist is denied.
        ProviderNotFound: If the source service URL is invalid.
        RateLimited: If rate limit is exceeded.
        InvalidProviderResponse: If provider returns malformed data.
        TemporaryProviderFailure: If provider is temporarily unavailable.
        CancellationRequested: If operation is cancelled.
    """
    # Get job from repository
    job = dependencies.jobs.get(job_id)
    if job is None:
        raise JobNotFoundError(job_id)

    # Check lease token
    if job.lease_token != lease_token:
        raise LeaseLostError(job_id)

    # Check for cancellation before starting
    cancel.raise_if_cancelled()

    # 120.01: Update job state to reading and emit event
    dependencies.jobs.update_status(job_id, JobStatus.READING)

    # Emit SourceProgressEvent with initial state
    emit(SourceProgressEvent(
        type="source_progress",
        job_id=job_id,
        total_source_items=0,
        loaded_count=0,
        normalized_count=0,
        skipped_count=0,
        timestamp=datetime.now(timezone.utc).isoformat(),
    ))

    # 120.02: Load source playlist using the complete-load method
    # Create playlist reference from request
    reference = PlaylistReference(
        service=request.source_service,
        playlist_id=request.source_playlist_id,
    )

    # Load the complete playlist using the source adapter
    loaded_playlist = dependencies.source_adapter.load_playlist(
        reference=reference,
        cancel=cancel,
    )

    # Emit updated SourceProgressEvent with loaded count
    emit(SourceProgressEvent(
        type="source_progress",
        job_id=job_id,
        total_source_items=loaded_playlist.metadata.item_count,
        loaded_count=len(loaded_playlist.tracks),
        normalized_count=len(loaded_playlist.tracks),
        skipped_count=0,
        timestamp=datetime.now(timezone.utc).isoformat(),
    ))

    # Return the loaded playlist
    return loaded_playlist


def accepted_uris_in_source_order(
    tracks: Sequence[SourceTrack],
    decisions: Sequence[MatchDecision],
) -> list[str]:
    """Extract accepted URIs from decisions in source playlist order.

    This function returns the URIs of accepted Spotify candidates in the order
    they appear in the source playlist. Tracks that are unmatched, unavailable,
    skipped, or ambiguous are omitted.

    Args:
        tracks: Sequence of SourceTrack objects in source playlist order.
        decisions: Sequence of MatchDecision objects for the tracks.

    Returns:
        List of Spotify URIs in source order.

    Examples:
        >>> from playlist_bridge.domain.models import MatchScore, SpotifyCandidate, SourceTrack, MatchDecision
        >>> track1 = SourceTrack(
        ...     position=0,
        ...     title="Song 1",
        ...     artist_names=["Artist 1"],
        ...     duration_seconds=180,
        ...     video_id="abc123",
        ...     availability="available",
        ... )
        >>> candidate1 = SpotifyCandidate(
        ...     track_id="xyz789",
        ...     uri="spotify:track:xyz789",
        ...     title="Song 1",
        ...     artist_names=["Artist 1"],
        ...     album="Album 1",
        ...     duration_seconds=180,
        ...     explicit=False,
        ... )
        >>> score1 = MatchScore(
        ...     title_similarity=0.95,
        ...     artist_similarity=0.9,
        ...     duration_similarity=1.0,
        ...     version_agreement=1.0,
        ...     unwanted_version_penalty=0.0,
        ...     explicit_state=1.0,
        ...     total_score=0.95,
        ...     reasons=["Good match"],
        ... )
        >>> decision1 = MatchDecision(
        ...     source_item_id="abc123",
        ...     status="matched",
        ...     selected_candidate=candidate1,
        ...     match_score=score1,
        ... )
        >>> track2 = SourceTrack(
        ...     position=1,
        ...     title="Song 2",
        ...     artist_names=["Artist 2"],
        ...     duration_seconds=200,
        ...     video_id="def456",
        ...     availability="available",
        ... )
        >>> decision2 = MatchDecision(
        ...     source_item_id="def456",
        ...     status="unmatched",
        ...     selected_candidate=None,
        ...     match_score=None,
        ... )
        >>> accepted_uris_in_source_order([track1, track2], [decision1, decision2])
        ['spotify:track:xyz789']
    """
    # Build lookup from source_item_id to decision
    decision_lookup: dict[str, MatchDecision] = {}
    for decision in decisions:
        if decision.source_item_id in decision_lookup:
            # Duplicate decisions for same source item - keep the first one
            # For duplicate source items, this preserves the first decision
            continue
        decision_lookup[decision.source_item_id] = decision

    # Iterate through tracks in source order
    result: list[str] = []
    for track in tracks:
        # Use video_id as the source_item_id
        source_id = track.video_id
        decision = decision_lookup.get(source_id)

        # If no decision found, skip this track (unmatched)
        if decision is None:
            continue

        # Skip unavailable tracks regardless of decision
        # availability might be a TrackStatus enum or a string
        avail = track.availability
        if hasattr(avail, "value"):
            avail = avail.value
        if avail == "unavailable":
            continue

        # Check if the decision is accepted
        # Accepted means status == "matched" and selected_candidate is not None
        if decision.status == "matched" and decision.selected_candidate is not None:
            result.append(decision.selected_candidate.uri)
        # Otherwise skip: unavailable, skipped, ambiguous, unmatched
        # The decision status indicates these states

    return result
