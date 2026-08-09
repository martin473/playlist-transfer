"""JSONL event models for the playlist bridge.

These models define the structured events emitted during a transfer job,
including job lifecycle events, progress updates, and outcome events.
Each event is a discriminated Pydantic model with a literal 'type' field.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class JobStartedEvent(BaseModel):
    """Emitted when a transfer job begins execution.

    Attributes:
        type: Literal event type discriminator ('job_start').
        job_id: Unique identifier of the job.
        source_service: Source service type ('youtube' or 'spotify').
        destination_service: Destination service type ('youtube' or 'spotify').
        source_playlist_id: Identifier of the source playlist in its service.
        destination_playlist_name: Name of the destination playlist.
        mode: Transfer mode ('create', 'merge', or 'replace').
        policy: Match policy ('strict', 'balanced', or 'loose').
        dry_run: Whether the job is running in dry-run mode.
        timestamp: ISO 8601 timestamp when the job started.
    """

    type: Literal["job_start"] = Field(description="Event type discriminator")
    job_id: str = Field(description="Unique job identifier")
    source_service: Literal["youtube", "spotify"] = Field(description="Source service type")
    destination_service: Literal["youtube", "spotify"] = Field(description="Destination service type")
    source_playlist_id: str = Field(description="Source playlist identifier")
    destination_playlist_name: str = Field(description="Destination playlist name")
    mode: Literal["create", "merge", "replace"] = Field(description="Transfer mode")
    policy: Literal["strict", "balanced", "loose"] = Field(description="Match policy")
    dry_run: bool = Field(description="Whether running in dry-run mode")
    timestamp: str = Field(description="ISO 8601 timestamp")


class WriteProgressEvent(BaseModel):
    """Emitted as matched tracks are written to the destination playlist.

    Attributes:
        type: Literal event type discriminator ('write_progress').
        job_id: Unique identifier of the job.
        total_to_write: Total number of tracks to write.
        written_count: Number of tracks written so far.
        skipped_count: Number of tracks skipped during write.
        timestamp: ISO 8601 timestamp when this event was emitted.
    """

    type: Literal["write_progress"] = Field(description="Event type discriminator")
    job_id: str = Field(description="Unique job identifier")
    total_to_write: int = Field(description="Total tracks to write")
    written_count: int = Field(description="Number of tracks written so far")
    skipped_count: int = Field(description="Number of tracks skipped during write")
    timestamp: str = Field(description="ISO 8601 timestamp")


class SourceProgressEvent(BaseModel):
    """Emitted as source playlist items are loaded and normalized.

    Attributes:
        type: Literal event type discriminator ('source_progress').
        job_id: Unique identifier of the job.
        total_source_items: Total number of items in the source playlist.
        loaded_count: Number of items loaded so far.
        normalized_count: Number of items successfully normalized.
        skipped_count: Number of items skipped (non-track, unavailable, etc.).
        timestamp: ISO 8601 timestamp when this event was emitted.
    """

    type: Literal["source_progress"] = Field(description="Event type discriminator")
    job_id: str = Field(description="Unique job identifier")
    total_source_items: int = Field(description="Total items in source playlist")
    loaded_count: int = Field(description="Number of items loaded so far")
    normalized_count: int = Field(description="Number of items normalized")
    skipped_count: int = Field(description="Number of items skipped")
    timestamp: str = Field(description="ISO 8601 timestamp")


class MatchProgressEvent(BaseModel):
    """Emitted as source tracks are matched to destination candidates.

    Attributes:
        type: Literal event type discriminator ('match_progress').
        job_id: Unique identifier of the job.
        total_tracks: Total number of tracks to match.
        matched_count: Number of tracks matched so far.
        reviewed_count: Number of tracks requiring review.
        skipped_count: Number of tracks skipped (no candidates, etc.).
        timestamp: ISO 8601 timestamp when this event was emitted.
    """

    type: Literal["match_progress"] = Field("match_progress", description="Event type discriminator")
    job_id: str = Field(description="Unique job identifier")
    total_tracks: int = Field(description="Total tracks to match")
    matched_count: int = Field(description="Number of tracks matched so far")
    reviewed_count: int = Field(description="Number of tracks requiring review")
    skipped_count: int = Field(description="Number of tracks skipped")
    timestamp: str = Field(description="ISO 8601 timestamp")


class VerificationProgressEvent(BaseModel):
    """Emitted as destination playlist content is verified.

    Attributes:
        type: Literal event type discriminator ('verification_progress').
        job_id: Unique identifier of the job.
        total_to_verify: Total number of tracks to verify.
        verified_count: Number of tracks verified so far.
        mismatched_count: Number of tracks that don't match expected content.
        missing_count: Number of tracks that could not be found.
        timestamp: ISO 8601 timestamp when this event was emitted.
    """

    type: Literal["verification_progress"] = Field(description="Event type discriminator")
    job_id: str = Field(description="Unique job identifier")
    total_to_verify: int = Field(description="Total tracks to verify")
    verified_count: int = Field(description="Number of tracks verified so far")
    mismatched_count: int = Field(description="Number of tracks that don't match")
    missing_count: int = Field(description="Number of tracks not found")
    timestamp: str = Field(description="ISO 8601 timestamp")


class FailureEvent(BaseModel):
    """Emitted when a transfer job fails.

    Attributes:
        type: Literal event type discriminator ('failure').
        job_id: Unique identifier of the job.
        error_type: Type of error that occurred.
        error_message: Human-readable error message.
        step: Optional step during which the failure occurred.
        timestamp: ISO 8601 timestamp when the failure was emitted.
    """

    type: Literal["failure"] = Field(description="Event type discriminator")
    job_id: str = Field(description="Unique job identifier")
    error_type: str = Field(description="Type of error that occurred")
    error_message: str = Field(description="Human-readable error message")
    step: Optional[str] = Field(default=None, description="Step during which the failure occurred")
    timestamp: str = Field(description="ISO 8601 timestamp")


# Module-level aliases for verification tests
failure = FailureEvent
type = type

