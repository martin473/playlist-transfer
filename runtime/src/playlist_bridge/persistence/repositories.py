"""Repository functions for playlist-bridge persistence."""

from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session

from playlist_bridge.domain.models import AccountProfile, MatchDecision, SourceTrack, TransferRequest
from playlist_bridge.domain.enums import DestinationService, JobStatus, SourceService, TrackStatus
from playlist_bridge.persistence.models import AccountProfileRecord, JobRecord, ManualCorrection, MatchCacheEntry, MatchDecisionRecord, SourceTrackRecord
from playlist_bridge.ports import IntegrityError


class JobNotFoundError(Exception):
    """Raised when a job with the given ID does not exist."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Job not found: {job_id}")


class LeaseLostError(Exception):
    """Raised when a lease is lost (e.g., stale takeover, expired)."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Lease lost for job: {job_id}")


class JobLease:
    """Represents a lease on a job for compare-and-swap operations.

    Attributes:
        lease_holder: The identifier of the lease holder (e.g., process ID).
        lease_expires_at: The timestamp when the lease expires.
        lease_heartbeat_at: The timestamp of the last heartbeat.
    """

    def __init__(
        self,
        lease_holder: str,
        lease_expires_at: datetime,
        lease_heartbeat_at: datetime,
    ) -> None:
        self.lease_holder = lease_holder
        self.lease_expires_at = lease_expires_at
        self.lease_heartbeat_at = lease_heartbeat_at


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
    """Retrieve a job by its ID.

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


def update_job_checkpoint(
    session: Session,
    job_id: str,
    checkpoint_fields: Mapping[str, Any],
    updated_at: datetime,
    *,
    lease: JobLease,
) -> JobRecord:
    """Update only documented checkpoint fields in one transaction.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        checkpoint_fields: Mapping of checkpoint field names to new values.
            Valid fields: "match_checkpoint", "write_checkpoint", "verification_checkpoint".
        updated_at: Updated timestamp (timezone-aware).
        lease: JobLease instance containing lease holder, expiration, and heartbeat.

    Returns:
        The updated JobRecord instance.

    Raises:
        JobNotFoundError: If no job exists with the given job_id.
        LeaseLostError: If the lease is lost (stale takeover or expired).

    Side Effects:
        sqlite_read, sqlite_write: Updates the job's checkpoint fields, updated_at,
        lease_holder, lease_expires_at, and lease_heartbeat_at.

    Note:
        This function commits the transaction. Caller should wrap in a transaction
        and handle errors appropriately.
    """
    # Load the job with a row lock to prevent concurrent updates
    job = session.query(JobRecord).filter_by(id=job_id).with_for_update().first()
    if job is None:
        raise JobNotFoundError(job_id)

    # Verify the lease is valid (compare-and-swap)
    # Check if the lease holder matches and the lease hasn't expired
    if job.lease_holder != lease.lease_holder:
        raise LeaseLostError(job_id)

    # If there's an expiration time, check if it's still valid
    # Note: SQLite doesn't store timezone info, so the stored value is naive
    # We compare against a naive UTC datetime for consistency
    if job.lease_expires_at is not None and job.lease_expires_at < datetime.now(timezone.utc).replace(tzinfo=None):
        raise LeaseLostError(job_id)

    # Update only the provided checkpoint fields
    valid_checkpoint_fields = {"match_checkpoint", "write_checkpoint", "verification_checkpoint"}
    for field_name, value in checkpoint_fields.items():
        if field_name not in valid_checkpoint_fields:
            raise ValueError(
                f"Invalid checkpoint field: {field_name}. "
                f"Must be one of: {', '.join(sorted(valid_checkpoint_fields))}"
            )
        setattr(job, field_name, value)

    # Update the timestamp and lease information
    job.updated_at = updated_at
    job.lease_holder = lease.lease_holder
    job.lease_expires_at = lease.lease_expires_at
    job.lease_heartbeat_at = lease.lease_heartbeat_at

    # Increment row version for optimistic locking
    job.row_version += 1

    session.commit()
    return job


def record_job_error(
    session: Session,
    job_id: str,
    safe_code: str,
    safe_message: str,
    updated_at: datetime,
) -> JobRecord:
    """Store one safe error summary without credential text.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        safe_code: Error code (e.g., "SPOTIFY_404", "YOUTUBE_403").
        safe_message: Human-readable error message (must not contain credentials).
        updated_at: Updated timestamp (timezone-aware).

    Returns:
        The updated JobRecord instance with last_error set.

    Raises:
        JobNotFoundError: If no job exists with the given job_id.
        ValueError: If safe_code or safe_message is empty or contains credential-like text.

    Side Effects:
        sqlite_read, sqlite_write: Updates the job's last_error and updated_at fields.
    """
    # Validate inputs
    if not safe_code or not safe_code.strip():
        raise ValueError("safe_code cannot be empty or whitespace only")
    if not safe_message or not safe_message.strip():
        raise ValueError("safe_message cannot be empty or whitespace only")

    # Security: Reject credential-like patterns
    credential_patterns = [
        "secret", "token", "password", "passwd", "api_key", "apikey",
        "auth", "authorization", "bearer", "oauth", "client_secret",
        "key", "credential", "private", "-----BEGIN", "-----END",
    ]
    safe_message_lower = safe_message.lower()
    for pattern in credential_patterns:
        if pattern in safe_message_lower:
            raise ValueError(f"safe_message contains credential-like pattern: '{pattern}'")

    # Find and update the job
    job = session.query(JobRecord).filter_by(id=job_id).first()
    if job is None:
        raise JobNotFoundError(job_id)

    # Format the error with code and message
    job.last_error = f"[{safe_code}] {safe_message}"
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


def upsert_match_decision(
    session: Session,
    job_id: str,
    decision: MatchDecision,
) -> MatchDecision:
    """Insert or update a match decision for a specific job and source item.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        decision: MatchDecision domain object to persist.

    Returns:
        The persisted MatchDecision domain object.

    Raises:
        JobNotFoundError: If the job with the given ID does not exist.
        IntegrityError: If a database integrity constraint is violated.

    Side Effects:
        sqlite_read, sqlite_write: Updates or inserts the match decision record.

    Note:
        This function commits the transaction. Caller should wrap in a transaction
        and handle errors appropriately.
    """
    # Check if the job exists
    job_exists = session.query(JobRecord).filter_by(id=job_id).first()
    if job_exists is None:
        raise JobNotFoundError(job_id)

    # Map domain status to persistence status
    status_mapping = {
        "matched": "accepted",
        "unmatched": "rejected",
    }
    decision_status = status_mapping.get(decision.status, "pending")

    # Extract spotify_track_id from selected_candidate if status is "matched"
    spotify_track_id = None
    if decision.status == "matched" and decision.selected_candidate:
        spotify_track_id = decision.selected_candidate.track_id

    # Serialize score to dict
    score_json = {}
    if decision.score:
        score_json = decision.score.model_dump()
    # Add reason to score_json
    if decision.reason:
        score_json["reason"] = decision.reason

    # Check if a decision already exists for this job and source item
    existing = session.query(MatchDecisionRecord).filter_by(
        job_id=job_id,
        source_item_id=decision.source_item_id,
    ).first()

    if existing:
        # Update the existing record
        existing.spotify_track_id = spotify_track_id
        existing.score_json = score_json
        existing.decision_status = decision_status
        # reviewed field: keep existing value
        session.commit()
    else:
        # Create a new record
        record = MatchDecisionRecord(
            job_id=job_id,
            source_item_id=decision.source_item_id,
            spotify_track_id=spotify_track_id,
            score_json=score_json,
            decision_status=decision_status,
            reviewed=False,
        )
        try:
            session.add(record)
            session.commit()
        except SQLAlchemyIntegrityError as e:
            session.rollback()
            raise IntegrityError(f"Integrity constraint violated: {e}") from e

    return decision


def get_unresolved_decisions(session: Session, job_id: str) -> list[MatchDecision]:
    """Retrieve unresolved match decisions for a job in source order.

    Unresolved decisions are those with decision_status not in ['accepted', 'skipped'].
    The results are ordered by the source track position.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.

    Returns:
        A list of MatchDecision domain objects for unresolved decisions,
        ordered by source position ascending.

    Raises:
        JobNotFoundError: If the job with the given ID does not exist.

    Side Effects:
        read-only: This function does not modify the database.
    """
    # Check if the job exists
    job_exists = session.query(JobRecord).filter_by(id=job_id).first()
    if job_exists is None:
        raise JobNotFoundError(job_id)

    # Query unresolved decisions with source track join for ordering
    from sqlalchemy import asc

    records = (
        session.query(MatchDecisionRecord)
        .join(
            SourceTrackRecord,
            (MatchDecisionRecord.job_id == SourceTrackRecord.job_id)
            & (MatchDecisionRecord.source_item_id == SourceTrackRecord.source_item_id),
        )
        .filter(MatchDecisionRecord.job_id == job_id)
        .filter(MatchDecisionRecord.decision_status.notin_(["accepted", "skipped"]))
        .order_by(asc(SourceTrackRecord.position))
        .all()
    )

    # Convert ORM records to domain MatchDecision objects using the new domain model
    from playlist_bridge.domain.models import MatchScore, SpotifyCandidate

    decisions = []
    for record in records:
        score_data = record.score_json
        track_id = record.spotify_track_id

        # Build SpotifyCandidate if we have a track_id
        selected_candidate = None
        if track_id:
            selected_candidate = SpotifyCandidate(
                track_id=track_id,
                uri=f"spotify:track:{track_id}",
                title=score_data.get("destination_title", track_id),
                artist_names=score_data.get("destination_artist_names", ["Unknown Artist"]),
                album=score_data.get("album", "Unknown Album"),
                duration_seconds=score_data.get("duration_seconds", 0),
                explicit=score_data.get("explicit", False),
            )

        # Build MatchScore from score_data
        match_score = None
        if score_data:
            match_score = MatchScore(
                title_similarity=score_data.get("title_similarity", 0.0),
                artist_similarity=score_data.get("artist_similarity", 0.0),
                duration_similarity=score_data.get("duration_similarity", 0.0),
                version_agreement=score_data.get("version_agreement", 1.0),
                unwanted_version_penalty=score_data.get("unwanted_version_penalty", 1.0),
                explicit_state=score_data.get("explicit_state", 1.0),
                total_score=score_data.get("total_score", 0.0),
                reasons=score_data.get("reasons", []),
            )

        # Map persistence status to domain status
        status_mapping = {
            "accepted": "matched",
            "rejected": "unmatched",
            "pending": "matched",
            "review": "matched",
        }
        status = status_mapping.get(record.decision_status, "matched")

        reason = score_data.get("reason", f"Decision: {record.decision_status}")

        decision = MatchDecision(
            source_item_id=record.source_item_id,
            status=status,
            selected_candidate=selected_candidate,
            score=match_score,
            reason=reason,
        )
        decisions.append(decision)

    return decisions


def save_profile(session: Session, profile: AccountProfile) -> AccountProfile:
    """Save or update an account profile.

    Args:
        session: SQLAlchemy Session instance.
        profile: AccountProfile domain object to save.

    Returns:
        The saved AccountProfile object (with any updates applied).

    Side Effects:
        writes to database: This function modifies the database.
    """
    # Check if profile already exists using the correct field names
    existing = session.query(AccountProfileRecord).filter_by(
        service=profile.service,
        profile_name=profile.profile_name,
    ).first()

    if existing:
        # Update existing record
        existing.display_name = profile.display_name
        existing.provider_user_id = profile.provider_user_id
        existing.updated_at = datetime.now(timezone.utc)
        session.commit()
        # Return the updated profile
        return AccountProfile(
            profile_name=existing.profile_name,
            service=existing.service,
            provider_user_id=existing.provider_user_id,
            display_name=existing.display_name,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )
    else:
        # Create new record
        record = AccountProfileRecord(
            service=profile.service,
            profile_name=profile.profile_name,
            provider_user_id=profile.provider_user_id,
            display_name=profile.display_name,
        )
        session.add(record)
        session.commit()
        # Return the saved profile
        return AccountProfile(
            profile_name=record.profile_name,
            service=record.service,
            provider_user_id=record.provider_user_id,
            display_name=record.display_name,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )


def list_profiles(session: Session, service: str | None = None) -> list[AccountProfile]:
    """List all account profiles, optionally filtered by service.

    Args:
        session: SQLAlchemy Session instance.
        service: Optional service name to filter by.

    Returns:
        A list of AccountProfile domain objects ordered by service then profile_name.

    Side Effects:
        read-only: This function does not modify the database.
    """
    query = session.query(AccountProfileRecord)
    if service is not None:
        query = query.filter_by(service=service)
    records = query.order_by(AccountProfileRecord.service, AccountProfileRecord.profile_name).all()

    profiles = []
    for record in records:
        profile = AccountProfile(
            profile_name=record.profile_name,
            service=record.service,
            provider_user_id=record.provider_user_id,
            display_name=record.display_name,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
        profiles.append(profile)

    return profiles


def get_profile(session: Session, service: str, profile_name: str) -> AccountProfile | None:
    """Retrieve a specific account profile by service and profile name.

    Args:
        session: SQLAlchemy Session instance.
        service: Service name (e.g., 'spotify', 'youtube').
        profile_name: Profile name/account ID.

    Returns:
        AccountProfile if found, else None.

    Side Effects:
        read-only: This function does not modify the database.
    """
    record = session.query(AccountProfileRecord).filter_by(
        service=service,
        profile_name=profile_name,
    ).first()

    if record is None:
        return None

    profile = AccountProfile(
        profile_name=record.profile_name,
        service=record.service,
        provider_user_id=record.provider_user_id,
        display_name=record.display_name,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )

    return profile


def list_recent_jobs(session: Session, limit: int = 20) -> list[JobRecord]:
    """Return recent jobs in deterministic recency order.

    Args:
        session: SQLAlchemy Session instance.
        limit: Maximum number of jobs to return. Defaults to 20.

    Returns:
        A list of JobRecord objects ordered by created_at descending,
        then by id descending for deterministic ordering.

    Raises:
        ValueError: If limit is less than 1.

    Side Effects:
        read-only: This function does not modify the database.
    """
    if limit < 1:
        raise ValueError("limit must be at least 1")

    records = session.query(JobRecord).order_by(
        JobRecord.created_at.desc(),
        JobRecord.id.desc(),
    ).limit(limit).all()

    return records


def resolve_correction_then_cache(session: Session, fingerprint: str) -> ManualCorrection | MatchCacheEntry | None:
    """Resolve a fingerprint by checking manual correction before automatic cache.

    This resolver checks for a manual correction first. If found, it returns the
    ManualCorrection. If not, it checks the automatic match cache. If found,
    it returns the MatchCacheEntry. If neither exists, returns None.

    Args:
        session: SQLAlchemy Session instance.
        fingerprint: Canonical source track fingerprint string.

    Returns:
        ManualCorrection if a manual correction exists for the fingerprint,
        MatchCacheEntry if an automatic cache entry exists,
        None if neither exists.

    Side Effects:
        read-only: This function does not modify the database.
    """
    # Check manual correction first
    correction = lookup_manual_correction(session, fingerprint)
    if correction is not None:
        return correction

    # Fall back to automatic cache
    return lookup_match_cache(session, fingerprint)
