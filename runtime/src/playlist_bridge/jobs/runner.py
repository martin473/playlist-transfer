"""Job runner and job ID generation for playlist-bridge."""

import json
import uuid
from typing import NamedTuple, Sequence, TextIO, Union

from playlist_bridge.domain.events import JobEvent, JobEventAdapter
from playlist_bridge.domain.models import SourceTrack, MatchDecision, SpotifyCandidate


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
        ...     score=score1,
        ...     reason="Good match",
        ... )
        >>> counts = calculate_transfer_counts([track1], [decision1])
        >>> counts.matched
        1
        >>> counts.unmatched
        0
    """
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

        # Use status and selected_candidate to determine the outcome
        # For "matched" status with selected_candidate, count as matched
        if decision.status == "matched" and decision.selected_candidate is not None:
            matched += 1
        elif decision.status == "unmatched":
            # If status is explicitly unmatched, count as unmatched
            unmatched += 1
        else:
            # Fallback: if status is unknown, check if there's a selected_candidate
            if decision.selected_candidate is not None:
                matched += 1
            else:
                unmatched += 1

    return TransferCounts(
        matched=matched,
        ambiguous=ambiguous,
        unmatched=unmatched,
        unavailable=unavailable,
        skipped=skipped,
        non_track=non_track,
    )


def accepted_uris_in_source_order(
    tracks: Sequence[SourceTrack],
    decisions: Sequence[MatchDecision],
) -> list[str]:
    """Return accepted Spotify URIs in source position order.

    This function filters source tracks by their match decisions, returning only
    accepted tracks (those with status == "matched" and selected_candidate present)
    while excluding unavailable, skipped, ambiguous, and unmatched items. The results
    maintain the original source playlist order, and duplicate source items remain
    duplicated unless a later explicit deduplication option is enabled.

    Args:
        tracks: Sequence of SourceTrack objects in source playlist order.
        decisions: Sequence of MatchDecision objects for the tracks.

    Returns:
        List of Spotify URIs for accepted tracks, in source position order.

    Raises:
        ValueError: If tracks or decisions are invalid (e.g., mismatched).

    Examples:
        >>> from playlist_bridge.domain.models import MatchScore, SpotifyCandidate
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
        >>> track1 = SourceTrack(
        ...     position=0,
        ...     title="Song 1",
        ...     artist_names=["Artist 1"],
        ...     duration_seconds=180,
        ...     video_id="abc123",
        ...     availability="available",
        ... )
        >>> track2 = SourceTrack(
        ...     position=1,
        ...     title="Song 2",
        ...     artist_names=["Artist 2"],
        ...     duration_seconds=200,
        ...     video_id="def456",
        ...     availability="available",
        ... )
        >>> decision1 = MatchDecision(
        ...     source_item_id="abc123",
        ...     status="matched",
        ...     selected_candidate=candidate1,
        ...     score=score1,
        ...     reason="Good match",
        ... )
        >>> decision2 = MatchDecision(
        ...     source_item_id="def456",
        ...     status="unmatched",
        ...     reason="No suitable match",
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
