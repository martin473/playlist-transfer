"""Repository functions for playlist-bridge persistence."""

from datetime import datetime
from typing import Sequence

from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from playlist_bridge.domain.models import SourceTrack, TransferRequest
from playlist_bridge.persistence.models import JobRecord, MatchCacheEntry, SourceTrackRecord
from playlist_bridge.ports import IntegrityError


class JobNotFoundError(Exception):
    """Raised when a job with the given ID does not exist."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Job not found: {job_id}")


def lookup_match_cache(session: Session, fingerprint: str) -> MatchCacheEntry | None:
    """Look up one automatic match by canonical fingerprint.

    Args:
        session: SQLAlchemy Session instance.
        fingerprint: Canonical source track fingerprint string.

    Returns:
        MatchCacheEntry if found, else None.
    """
    return session.query(MatchCacheEntry).filter_by(source_fingerprint=fingerprint).first()


def create_job(
    session: Session,
    request: TransferRequest,
    job_id: str,
    created_at: datetime,
) -> JobRecord:
    """Create a new job record from a transfer request.

    Args:
        session: SQLAlchemy Session instance.
        request: TransferRequest domain model containing transfer parameters.
        job_id: Unique identifier for the job (e.g., UUID string).
        created_at: Creation timestamp (timezone-aware).

    Returns:
        The created JobRecord instance.

    Raises:
        IntegrityError: If a job with the same job_id already exists.

    Note:
        This function commits the transaction. Caller should wrap in a transaction
        and handle IntegrityError appropriately.
    """
    # Extract source/destination playlist IDs based on transfer mode
    source_playlist_id = request.source_playlist_id
    destination_playlist_id = request.destination_playlist_id

    # Convert request to JSON for storage
    request_json = request.model_dump(mode="json")

    # Create the job record
    job = JobRecord(
        id=job_id,
        request_json=request_json,
        state="pending",  # Initial state
        source_playlist_id=source_playlist_id,
        destination_playlist_id=destination_playlist_id,
        source_track_count=None,  # Not known yet
        match_checkpoint=0,
        write_checkpoint=0,
        verification_checkpoint=0,
        created_at=created_at,
        updated_at=created_at,
        last_error=None,
        lease_holder=None,
        lease_expires_at=None,
        lease_heartbeat_at=None,
        row_version=1,
    )

    session.add(job)
    session.commit()

    return job


def bulk_insert_source_tracks(
    session: Session,
    job_id: str,
    tracks: Sequence[SourceTrack],
) -> int:
    """Insert an ordered collection of source tracks for one job in one transaction.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        tracks: Sequence of SourceTrack domain objects in ascending position order.

    Returns:
        The number of rows inserted.

    Raises:
        JobNotFoundError: If the job with the given ID does not exist.
        IntegrityError: If a database integrity constraint is violated
            (e.g., duplicate source_item_id for the job).

    Note:
        This function commits the transaction. Caller should wrap in a transaction
        and handle errors appropriately.
    """
    # Check if the job exists
    job_exists = session.query(JobRecord).filter_by(id=job_id).first()
    if job_exists is None:
        raise JobNotFoundError(job_id)

    # Convert SourceTrack domain objects to SourceTrackRecord ORM objects
    records = []
    for track in tracks:
        record = SourceTrackRecord(
            job_id=job_id,
            source_item_id=track.video_id,  # Use video_id as the source item ID
            position=track.position,
            title=track.title,
            artist_names=track.artist_names,
            duration_seconds=track.duration_seconds,
            video_id=track.video_id,
            channel_title=track.channel_title,
        )
        records.append(record)

    # Bulk insert the records
    try:
        session.add_all(records)
        session.commit()
    except SQLAlchemyIntegrityError as e:
        session.rollback()
        # Re-raise as domain IntegrityError
        raise IntegrityError(f"Integrity constraint violated: {e}") from e

    return len(records)
