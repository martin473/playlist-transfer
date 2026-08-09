"""Repository functions for playlist-bridge persistence."""

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from playlist_bridge.domain.models import AccountProfile, MatchDecision, SourceTrack, TransferRequest
from playlist_bridge.domain.enums import DestinationService, JobStatus, SourceService
from playlist_bridge.persistence.models import AccountProfileRecord, JobRecord, ManualCorrection, MatchCacheEntry, MatchDecisionRecord, SourceTrackRecord
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


def upsert_match_cache(session: Session, entry: MatchCacheEntry) -> MatchCacheEntry:
    """Insert or update one automatic cache entry.

    Args:
        session: SQLAlchemy Session instance.
        entry: MatchCacheEntry instance to insert or update.

    Returns:
        The persisted MatchCacheEntry instance (with updated timestamps).

    Raises:
        IntegrityError: If a database integrity constraint is violated.

    Note:
        This function uses an upsert pattern: if a record with the same
        source_fingerprint exists, it updates the existing record; otherwise
        it inserts a new record. The function commits the transaction.
    """
    # Check if an entry with this fingerprint already exists
    existing = session.query(MatchCacheEntry).filter_by(
        source_fingerprint=entry.source_fingerprint
    ).first()

    if existing:
        # Update the existing entry with new values
        existing.spotify_track_id = entry.spotify_track_id
        existing.confidence = entry.confidence
        existing.origin = entry.origin
        existing.last_verified_at = entry.last_verified_at
        # updated_at will be updated automatically via onupdate
        session.commit()
        return existing
    else:
        # Insert new entry
        try:
            session.add(entry)
            session.commit()
        except SQLAlchemyIntegrityError as e:
            session.rollback()
            raise IntegrityError(f"Integrity constraint violated: {e}") from e
        return entry


def lookup_manual_correction(session: Session, fingerprint: str) -> ManualCorrection | None:
    """Look up one manual correction by canonical fingerprint.

    Args:
        session: SQLAlchemy Session instance.
        fingerprint: Canonical source track fingerprint string.

    Returns:
        ManualCorrection if found, else None.
    """
    return session.query(ManualCorrection).filter_by(source_fingerprint=fingerprint).first()


def upsert_manual_correction(session: Session, correction: ManualCorrection) -> ManualCorrection:
    """Insert or replace one manual correction.

    Args:
        session: SQLAlchemy Session instance.
        correction: ManualCorrection instance to insert or update.

    Returns:
        The persisted ManualCorrection instance (with updated timestamps).

    Raises:
        IntegrityError: If a database integrity constraint is violated.

    Note:
        This function uses an upsert pattern: if a record with the same
        source_fingerprint exists, it updates the existing record; otherwise
        it inserts a new record. The function commits the transaction.
    """
    # Check if a correction with this fingerprint already exists
    existing = session.query(ManualCorrection).filter_by(
        source_fingerprint=correction.source_fingerprint
    ).first()

    if existing:
        # Update the existing correction with new values
        existing.spotify_track_id = correction.spotify_track_id
        existing.skip_reason = correction.skip_reason
        existing.explanation = correction.explanation
        existing.origin = correction.origin
        # updated_at will be updated automatically via onupdate
        session.commit()
        # Return the existing record (with updated values and timestamps)
        return existing
    else:
        # Insert new correction
        try:
            session.add(correction)
            session.commit()
        except SQLAlchemyIntegrityError as e:
            session.rollback()
            raise IntegrityError(f"Integrity constraint violated: {e}") from e
        return correction


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


def get_job(session: Session, job_id: str) -> JobRecord | None:
    """Load one job by ID without mutating it.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.

    Returns:
        The JobRecord instance if found, else None.

    Side Effects:
        read-only: This function does not modify the database.
    """
    return session.query(JobRecord).filter_by(id=job_id).first()


def update_job_state(
    session: Session,
    job_id: str,
    status: JobStatus,
    updated_at: datetime,
) -> JobRecord:
    """Update the state of a job and its updated_at timestamp.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        status: New JobStatus to set.
        updated_at: Updated timestamp (timezone-aware).

    Returns:
        The updated JobRecord instance.

    Raises:
        JobNotFoundError: If no job exists with the given job_id.

    Side Effects:
        sqlite_read, sqlite_write: Updates the job's state and updated_at field.
    """
    job = session.query(JobRecord).filter_by(id=job_id).first()
    if job is None:
        raise JobNotFoundError(job_id)

    job.state = status.value
    job.updated_at = updated_at
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


def get_source_tracks_ordered(session: Session, job_id: str) -> list[SourceTrack]:
    """Retrieve source tracks for a job, ordered by source position.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.

    Returns:
        A list of SourceTrack domain objects ordered by position ascending.

    Raises:
        JobNotFoundError: If the job with the given ID does not exist.

    Side Effects:
        read-only: This function does not modify the database.
    """
    # Check if the job exists
    job_exists = session.query(JobRecord).filter_by(id=job_id).first()
    if job_exists is None:
        raise JobNotFoundError(job_id)

    # Query source tracks ordered by position
    records = session.query(SourceTrackRecord).filter_by(job_id=job_id).order_by(SourceTrackRecord.position.asc()).all()

    # Convert ORM records to domain SourceTrack objects
    return [
        SourceTrack(
            position=record.position,
            title=record.title,
            artist_names=record.artist_names,
            duration_seconds=record.duration_seconds,
            video_id=record.video_id,
            channel_title=record.channel_title,
        )
        for record in records
    ]


def save_profile(
    session: Session,
    profile: AccountProfile,
) -> AccountProfile:
    """Save an account profile to the database.

    Args:
        session: SQLAlchemy Session instance.
        profile: AccountProfile domain model to save.

    Returns:
        The saved AccountProfile instance (with any generated fields).

    Raises:
        IntegrityError: If a duplicate (service, profile_name) pair exists.

    Note:
        This function commits the transaction. Caller should wrap in a transaction
        and handle IntegrityError appropriately.
    """
    # Map service string from domain model (e.g., "spotify", "youtube")
    # to the format stored in the database (same string for now)
    service = profile.provider
    profile_name = profile.account_id  # Use account_id as the unique profile name
    # For display_name, use display_name from model
    display_name = profile.display_name

    # Check if a profile with this (service, profile_name) already exists
    existing = session.query(AccountProfileRecord).filter_by(
        service=service,
        profile_name=profile_name,
    ).first()

    if existing:
        # Update existing record
        existing.display_name = display_name
        existing.updated_at = datetime.now(timezone.utc)
        session.commit()
        # Return the updated profile
        return AccountProfile(
            provider=existing.service,
            account_id=existing.profile_name,
            display_name=existing.display_name,
            email=None,  # Not stored in this table
            username=None,  # Not stored in this table
            profile_url=None,  # Not stored in this table
        )
    else:
        # Create new record
        record = AccountProfileRecord(
            service=service,
            profile_name=profile_name,
            provider_user_id=profile_name,  # Use profile_name as provider_user_id for now
            display_name=display_name,
        )
        try:
            session.add(record)
            session.commit()
        except SQLAlchemyIntegrityError as e:
            session.rollback()
            raise IntegrityError(f"Integrity constraint violated: {e}") from e

    # Return the saved profile
    return AccountProfile(
        provider=service,
        account_id=profile_name,
        display_name=display_name,
        email=None,
        username=None,
        profile_url=None,
    )


def get_profile(
    session: Session,
    service: str,
    profile_name: str,
) -> AccountProfile | None:
    """Retrieve an account profile by service and profile name.

    Args:
        session: SQLAlchemy Session instance.
        service: The service provider (e.g., "spotify", "youtube").
        profile_name: The profile name (e.g., "default", "work").

    Returns:
        The AccountProfile instance, or None if not found.
    """
    record = session.query(AccountProfileRecord).filter_by(
        service=service,
        profile_name=profile_name,
    ).first()

    if record is None:
        return None

    return AccountProfile(
        provider=record.service,
        account_id=record.profile_name,
        display_name=record.display_name,
        email=None,
        username=None,
        profile_url=None,
    )


def list_profiles(
    session: Session,
    service: SourceService | DestinationService | None = None,
) -> list[AccountProfile]:
    """List account profiles, optionally filtered by service.

    Args:
        session: SQLAlchemy Session instance.
        service: If provided, only list profiles for this service (as a
                SourceService or DestinationService enum). If None, list all
                profiles across all services.

    Returns:
        A list of AccountProfile instances (empty list if none).
    """
    query = session.query(AccountProfileRecord)
    if service is not None:
        query = query.filter_by(service=service)

    records = query.order_by(AccountProfileRecord.service, AccountProfileRecord.profile_name).all()

    return [
        AccountProfile(
            provider=record.service,
            account_id=record.profile_name,
            display_name=record.display_name,
            email=None,
            username=None,
            profile_url=None,
        )
        for record in records
    ]


def upsert_match_decision(
    session: Session,
    job_id: str,
    decision: MatchDecision,
) -> MatchDecision:
    """Insert or replace a match decision for a job and source item.

    This function uses an upsert pattern: if a record with the same job_id
    and source_item_id exists, it updates the existing record; otherwise
    it inserts a new record. The transaction is committed automatically.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        decision: MatchDecision domain model containing the decision data.

    Returns:
        The persisted MatchDecision instance.

    Raises:
        JobNotFoundError: If the job with the given ID does not exist.
        IntegrityError: If a database integrity constraint is violated.
    """
    # Check if the job exists
    job_exists = session.query(JobRecord).filter_by(id=job_id).first()
    if job_exists is None:
        raise JobNotFoundError(job_id)

    # Check if a decision already exists for this job and source item
    existing = session.query(MatchDecisionRecord).filter_by(
        job_id=job_id,
        source_item_id=decision.source_item_id,
    ).first()

    if existing:
        # Update the existing record
        existing.spotify_track_id = decision.destination_track_id
        existing.score_json = {
            "score": decision.score,
            "confidence": decision.confidence,
            "decision_type": decision.decision_type,
        }
        existing.decision_status = decision.decision_type
        # reviewed field is not in MatchDecision domain model; keep existing value
        # updated_at will be updated automatically via onupdate
        session.commit()
        # Return the updated decision (using the same domain object)
        return decision
    else:
        # Create a new record
        record = MatchDecisionRecord(
            job_id=job_id,
            source_item_id=decision.source_item_id,
            spotify_track_id=decision.destination_track_id,
            score_json={
                "score": decision.score,
                "confidence": decision.confidence,
                "decision_type": decision.decision_type,
            },
            decision_status=decision.decision_type,
            reviewed=False,
        )
        try:
            session.add(record)
            session.commit()
        except SQLAlchemyIntegrityError as e:
            session.rollback()
            raise IntegrityError(f"Integrity constraint violated: {e}") from e

        return decision
