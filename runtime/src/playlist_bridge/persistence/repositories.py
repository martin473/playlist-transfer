"""Repository functions for playlist-bridge persistence."""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from typing import Any, Mapping, Sequence

from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session, sessionmaker

from playlist_bridge.domain.models import AccountProfile, MatchDecision, MatchScore, SourceTrack, SpotifyCandidate, TransferRequest
from playlist_bridge.domain.enums import DestinationService, JobStatus, SourceService, TrackStatus
from playlist_bridge.persistence.models import AccountProfileRecord, JobRecord, ManualCorrection, MatchCacheEntry, MatchDecisionRecord, SourceTrackRecord
from playlist_bridge.ports import IntegrityError


class JobNotFoundError(Exception):
    """Raised when a job with the given ID does not exist."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Job not found: {job_id}")


class JobLeaseBusyError(Exception):
    """Raised when a job lease cannot be acquired because it is held by another owner."""

    def __init__(self, job_id: str, owner_id: str) -> None:
        self.job_id = job_id
        self.owner_id = owner_id
        super().__init__(f"Job lease is held by another owner: {job_id} (owner: {owner_id})")


class LeaseLostError(Exception):
    """Raised when a lease is lost (e.g., stale takeover, expired)."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(f"Lease lost for job: {job_id}")


class JobLease:
    """Represents a lease on a job for compare-and-swap operations.

    This class provides both the contract-specified fields (job_id, owner_id,
    token, expires_at, row_version) and the fields needed by legacy checkpoint
    functions (lease_holder, lease_expires_at, lease_heartbeat_at).

    Attributes:
        job_id: The ID of the job this lease is for.
        owner_id: The identifier of the lease holder (e.g., process ID).
        token: The plaintext lease token (for reentrant acquisition).
        expires_at: The timestamp when the lease expires.
        row_version: The row version of the job record at lease acquisition.
        lease_heartbeat_at: The timestamp of the last heartbeat.
    """

    def __init__(
        self,
        job_id: str,
        owner_id: str,
        token: str,
        expires_at: datetime,
        row_version: int,
        lease_heartbeat_at: datetime,
    ) -> None:
        self.job_id = job_id
        self.owner_id = owner_id
        self.token = token
        self.expires_at = expires_at
        self.row_version = row_version
        self.lease_heartbeat_at = lease_heartbeat_at

    @property
    def lease_holder(self) -> str:
        """Legacy alias for owner_id."""
        return self.owner_id

    @property
    def lease_expires_at(self) -> datetime:
        """Legacy alias for expires_at."""
        return self.expires_at


def _compute_token_hash(token: str) -> str:
    """Compute a SHA-256 hash of a token string.

    Args:
        token: The plaintext token to hash.

    Returns:
        The hex digest of the SHA-256 hash.
    """
    return sha256(token.encode("utf-8")).hexdigest()


def _generate_lease_token() -> str:
    """Generate a secure random lease token.

    Returns:
        A 32-character hex string (16 bytes of random data).
    """
    return secrets.token_hex(16)


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
        # Update the existing entry with new values
        existing.spotify_track_id = correction.spotify_track_id
        existing.skip_reason = correction.skip_reason
        existing.explanation = correction.explanation
        existing.origin = correction.origin
        # updated_at will be updated automatically via onupdate
        session.commit()
        return existing
    else:
        # Insert new entry
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


def acquire_job_lease(
    session: Session,
    job_id: str,
    owner_id: str,
    now: datetime,
    lease_duration: timedelta,
    current_token: str | None = None,
) -> JobLease:
    """Atomically acquire a writer lease for a job.

    This function implements a compare-and-swap lease acquisition with
    reentrant support. If the caller already holds the lease (identified by
    the current_token), the lease is renewed. If the lease is held by another
    owner, the acquisition fails with JobLeaseBusyError.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        owner_id: Identifier of the process/runner acquiring the lease.
        now: Current timestamp (timezone-aware).
        lease_duration: Duration for which the lease is valid.
        current_token: If provided, the caller claims to already hold the lease.
            Used for reentrant acquisition (lease renewal).

    Returns:
        A JobLease instance containing the lease details, including the
        plaintext token for future reentrant acquisition.

    Raises:
        JobNotFoundError: If no job exists with the given job_id.
        JobLeaseBusyError: If the lease is held by a different owner and no
            current_token is provided or the token doesn't match.

    Side Effects:
        sqlite_read, sqlite_write, secure_random_token_generation:
        Reads the job record, generates a random token, and updates the
        job record with the new lease information and incremented row_version.
        All changes are committed atomically.

    Note:
        This function commits the transaction. The lease is valid until
        expires_at, and must be renewed by calling acquire_job_lease again
        with the current token before expiration.
    """
    # Lock the row for update to prevent race conditions
    job = session.query(JobRecord).filter_by(id=job_id).with_for_update().first()
    if job is None:
        raise JobNotFoundError(job_id)

    # Check if there's an existing lease
    existing_lease_holder = job.lease_holder
    existing_expires_at = job.lease_expires_at
    existing_lease_token_hash = getattr(job, "lease_token_hash", None)

    is_lease_expired = (
        existing_expires_at is not None and
        existing_expires_at.replace(tzinfo=timezone.utc) < now.replace(tzinfo=timezone.utc)
    )

    # If there's a valid lease (not expired) from a different owner
    if not is_lease_expired and existing_lease_holder is not None:
        if existing_lease_holder != owner_id:
            # If no current_token provided, the lease is busy
            if current_token is None:
                raise JobLeaseBusyError(job_id, existing_lease_holder)

            # If current_token is provided, verify it matches the stored hash
            current_token_hash = _compute_token_hash(current_token)
            if existing_lease_token_hash is None or existing_lease_token_hash != current_token_hash:
                raise JobLeaseBusyError(job_id, existing_lease_holder)

            # Token matches - this is a reentrant acquisition (lease renewal)
            # Generate a new token for the renewed lease
            new_token = _generate_lease_token()
            new_token_hash = _compute_token_hash(new_token)

            # Update the lease with new token and extended expiration
            job.lease_holder = owner_id
            if hasattr(job, "lease_token_hash"):
                job.lease_token_hash = new_token_hash
            job.lease_expires_at = now + lease_duration
            job.lease_heartbeat_at = now
            job.row_version += 1
            job.updated_at = now

            session.commit()

            # Return the new lease with the new token
            return JobLease(
                job_id=job_id,
                owner_id=owner_id,
                token=new_token,
                expires_at=now + lease_duration,
                row_version=job.row_version,
                lease_heartbeat_at=now,
            )

        # Same owner_id - this is a reentrant acquisition (lease renewal)
        # Generate a new token for the renewed lease
        new_token = _generate_lease_token()
        new_token_hash = _compute_token_hash(new_token)

        # Update the lease with new token and extended expiration
        job.lease_holder = owner_id
        if hasattr(job, "lease_token_hash"):
            job.lease_token_hash = new_token_hash
        job.lease_expires_at = now + lease_duration
        job.lease_heartbeat_at = now
        job.row_version += 1
        job.updated_at = now

        session.commit()

        return JobLease(
            job_id=job_id,
            owner_id=owner_id,
            token=new_token,
            expires_at=now + lease_duration,
            row_version=job.row_version,
            lease_heartbeat_at=now,
        )

    # No valid lease exists - acquire a new one
    new_token = _generate_lease_token()
    new_token_hash = _compute_token_hash(new_token)

    job.lease_holder = owner_id
    if hasattr(job, "lease_token_hash"):
        job.lease_token_hash = new_token_hash
    job.lease_expires_at = now + lease_duration
    job.lease_heartbeat_at = now
    job.row_version += 1
    job.updated_at = now

    session.commit()

    return JobLease(
        job_id=job_id,
        owner_id=owner_id,
        token=new_token,
        expires_at=now + lease_duration,
        row_version=job.row_version,
        lease_heartbeat_at=now,
    )


def release_job_lease(
    session: Session,
    lease: JobLease,
    now: datetime,
) -> bool:
    """Release a job lease.

    This function clears the lease fields only for the current owner/token pair
    and increments the row version in one transaction. Releasing an already
    absent lease is an explicit no-op result (returns False). A different owner
    cannot release the lease.

    Args:
        session: SQLAlchemy Session instance.
        lease: The current JobLease object containing the lease details.
        now: Current timestamp (timezone-aware).

    Returns:
        True if the lease was released (cleared), False if no lease was present.

    Raises:
        JobNotFoundError: If no job exists with the given lease.job_id.
        LeaseLostError: If the lease is stale - owner mismatch, token mismatch,
            or row version mismatch.

    Side Effects:
        sqlite_read, sqlite_write: Reads the job record, validates the lease,
        clears the lease fields, and increments row_version. All changes are
        committed atomically.
    """
    # Lock the row for update to prevent race conditions
    job = session.query(JobRecord).filter_by(id=lease.job_id).with_for_update().first()
    if job is None:
        raise JobNotFoundError(lease.job_id)

    # Check if there's no lease present
    if job.lease_holder is None:
        # Already released - this is an explicit no-op
        return False

    # Validate the lease matches the current state
    # Check owner
    if job.lease_holder != lease.owner_id:
        raise LeaseLostError(lease.job_id)

    # Check token hash
    token_hash = _compute_token_hash(lease.token)
    if job.lease_token_hash != token_hash:
        raise LeaseLostError(lease.job_id)

    # Check row version
    if job.row_version != lease.row_version:
        raise LeaseLostError(lease.job_id)

    # Check if the lease has expired
    if job.lease_expires_at is not None and job.lease_expires_at.replace(tzinfo=timezone.utc) < now.replace(tzinfo=timezone.utc):
        raise LeaseLostError(lease.job_id)

    # All checks passed - clear the lease fields
    job.lease_holder = None
    job.lease_expires_at = None
    job.lease_heartbeat_at = None
    job.lease_token_hash = None
    job.row_version += 1
    job.updated_at = now

    session.commit()

    return True


def heartbeat_job_lease(
    session: Session,
    lease: JobLease,
    now: datetime,
    lease_duration: timedelta,
) -> JobLease:
    """Extend a job lease with a heartbeat.

    This function extends the lease expiry by lease_duration seconds only when
    the job ID, owner, token hash, and expected row version match. It updates
    the heartbeat time and increments the row version in one transaction.

    The lease must be currently held by the caller. A stale token or row version
    cannot extend the lease.

    Args:
        session: SQLAlchemy Session instance.
        lease: The current JobLease object containing the lease details.
        now: Current timestamp (timezone-aware).
        lease_duration: Duration for which to extend the lease.

    Returns:
        An updated JobLease instance with the new expiration time,
        heartbeat time, and incremented row version.

    Raises:
        JobNotFoundError: If no job exists with the given lease.job_id.
        LeaseLostError: If the lease is stale - owner mismatch, token mismatch,
            or row version mismatch.

    Side Effects:
        sqlite_read, sqlite_write: Reads the job record and updates the
        lease expiration, heartbeat timestamp, row_version, and updated_at.
        All changes are committed atomically.
    """
    # Lock the row for update to prevent race conditions
    job = session.query(JobRecord).filter_by(id=lease.job_id).with_for_update().first()
    if job is None:
        raise JobNotFoundError(lease.job_id)

    # Validate the lease matches the current state
    # Check owner
    if job.lease_holder != lease.owner_id:
        raise LeaseLostError(lease.job_id)

    # Check token hash
    token_hash = _compute_token_hash(lease.token)
    if job.lease_token_hash != token_hash:
        raise LeaseLostError(lease.job_id)

    # Check row version
    if job.row_version != lease.row_version:
        raise LeaseLostError(lease.job_id)

    # All checks passed - extend the lease
    job.lease_expires_at = now + lease_duration
    job.lease_heartbeat_at = now
    job.row_version += 1
    job.updated_at = now

    session.commit()

    # Generate a new token for the extended lease
    new_token = _generate_lease_token()
    new_token_hash = _compute_token_hash(new_token)
    job.lease_token_hash = new_token_hash

    session.commit()

    return JobLease(
        job_id=lease.job_id,
        owner_id=lease.owner_id,
        token=new_token,
        expires_at=now + lease_duration,
        row_version=job.row_version,
        lease_heartbeat_at=now,
    )


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
        lease: JobLease instance containing lease holder, token, expiration, row version, and heartbeat.

    Returns:
        The updated JobRecord instance.

    Raises:
        JobNotFoundError: If no job exists with the given job_id.
        LeaseLostError: If the lease is lost (stale takeover, expired, token mismatch, or row version mismatch).

    Side Effects:
        sqlite_read, sqlite_write: Updates the job's checkpoint fields, updated_at,
        lease_holder, lease_expires_at, lease_heartbeat_at, lease_token_hash, and row_version.

    Note:
        This function commits the transaction. Caller should wrap in a transaction
        and handle errors appropriately.
    """
    # Load the job with a row lock to prevent concurrent updates
    job = session.query(JobRecord).filter_by(id=job_id).with_for_update().first()
    if job is None:
        raise JobNotFoundError(job_id)

    # Verify the lease is valid using compare-and-swap pattern
    # Check lease holder
    if job.lease_holder != lease.owner_id:
        raise LeaseLostError(job_id)

    # Check token hash
    token_hash = _compute_token_hash(lease.token)
    if job.lease_token_hash != token_hash:
        raise LeaseLostError(job_id)

    # Check row version
    if job.row_version != lease.row_version:
        raise LeaseLostError(job_id)

    # Check if the lease has expired
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
    job.lease_holder = lease.owner_id
    job.lease_expires_at = lease.expires_at
    job.lease_heartbeat_at = lease.lease_heartbeat_at

    # Generate a new token for the updated lease
    new_token = _generate_lease_token()
    new_token_hash = _compute_token_hash(new_token)
    job.lease_token_hash = new_token_hash

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
        safe_code: A short error code (e.g., "AUTH_FAILED", "RATE_LIMITED").
        safe_message: A user-facing error message that does not contain secrets.
        updated_at: Updated timestamp (timezone-aware).

    Returns:
        The updated JobRecord instance.

    Raises:
        JobNotFoundError: If no job exists with the given job_id.

    Side Effects:
        sqlite_read, sqlite_write: Updates the job's last_error, state, and updated_at.
    """
    job = session.query(JobRecord).filter_by(id=job_id).first()
    if job is None:
        raise JobNotFoundError(job_id)

    job.last_error = f"{safe_code}: {safe_message}"
    job.state = "failed"
    job.updated_at = updated_at
    session.commit()

    return job


def bulk_insert_source_tracks(
    session: Session,
    job_id: str,
    tracks: Sequence[SourceTrack],
) -> None:
    """Bulk insert source tracks for a job.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        tracks: Sequence of SourceTrack domain models to insert.

    Raises:
        IntegrityError: If a duplicate source_item_id is found for the job.

    Side Effects:
        sqlite_write: Inserts multiple source track records in a single
        transaction. Commits after all inserts.
    """
    if not tracks:
        return

    records = []
    for track in tracks:
        record = SourceTrackRecord(
            job_id=job_id,
            source_item_id=track.source_item_id,
            position=track.position,
            title=track.title,
            artist_names=track.artist_names,
            duration_seconds=track.duration_seconds,
            video_id=track.video_id,
            channel_title=track.channel_title,
        )
        records.append(record)

    try:
        session.add_all(records)
        session.commit()
    except SQLAlchemyIntegrityError as e:
        session.rollback()
        raise IntegrityError(f"Integrity constraint violated: {e}") from e


def get_source_tracks_ordered(
    session: Session,
    job_id: str,
    offset: int = 0,
    limit: int | None = None,
) -> Sequence[SourceTrackRecord]:
    """Retrieve source tracks for a job ordered by position.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        offset: Number of records to skip (default: 0).
        limit: Maximum number of records to return (default: None = no limit).

    Returns:
        A sequence of SourceTrackRecord objects ordered by position ascending.

    Side Effects:
        read-only: This function does not modify the database.
    """
    query = session.query(SourceTrackRecord).filter_by(job_id=job_id).order_by(SourceTrackRecord.position.asc())

    if offset > 0:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)

    return query.all()


def upsert_match_decision(
    session: Session,
    job_id: str,
    source_item_id: str,
    decision: MatchDecision,
) -> MatchDecisionRecord:
    """Insert or update a match decision for a source track.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        source_item_id: The ID of the source track.
        decision: MatchDecision domain model containing the decision data.

    Returns:
        The persisted MatchDecisionRecord instance.

    Raises:
        IntegrityError: If a database integrity constraint is violated.

    Side Effects:
        sqlite_write: Inserts or updates the match decision record.
        Commits the transaction.
    """
    # Extract data from domain model
    spotify_track_id = None
    if decision.selected_candidate:
        spotify_track_id = decision.selected_candidate.track_id

    # Build score_json from decision
    score_json: dict[str, Any] = {
        "status": decision.status,
        "reason": decision.reason,
    }
    if decision.score:
        score_json["score_details"] = decision.score.model_dump()
    if decision.selected_candidate:
        score_json["candidate"] = decision.selected_candidate.model_dump()
    if decision.ranked_alternatives:
        score_json["alternatives"] = [alt.model_dump() for alt in decision.ranked_alternatives]

    # Check if a decision already exists for this job/source_item_id
    existing = session.query(MatchDecisionRecord).filter_by(
        job_id=job_id,
        source_item_id=source_item_id,
    ).first()

    if existing:
        # Update existing record
        existing.spotify_track_id = spotify_track_id
        existing.score_json = score_json
        existing.decision_status = decision.status
        existing.reviewed = False  # Decision is not reviewed until explicitly reviewed
        # updated_at is automatically updated via onupdate
        session.commit()
        return existing
    else:
        # Insert new record
        record = MatchDecisionRecord(
            job_id=job_id,
            source_item_id=source_item_id,
            spotify_track_id=spotify_track_id,
            score_json=score_json,
            decision_status=decision.status,
            reviewed=False,
        )
        try:
            session.add(record)
            session.commit()
        except SQLAlchemyIntegrityError as e:
            session.rollback()
            raise IntegrityError(f"Integrity constraint violated: {e}") from e
        return record


def get_unresolved_decisions(
    session: Session,
    job_id: str,
    status_filter: Sequence[str] | None = None,
) -> Sequence[MatchDecisionRecord]:
    """Retrieve match decisions for a job filtered by decision status.

    Args:
        session: SQLAlchemy Session instance.
        job_id: Unique identifier for the job.
        status_filter: Optional list of decision status values to include.
            If None, returns all decisions.

    Returns:
        A sequence of MatchDecisionRecord objects for the job.

    Side Effects:
        read-only: This function does not modify the database.
    """
    query = session.query(MatchDecisionRecord).filter_by(job_id=job_id)

    if status_filter is not None:
        query = query.filter(MatchDecisionRecord.decision_status.in_(status_filter))

    return query.order_by(MatchDecisionRecord.id.asc()).all()


def list_recent_jobs(session: Session, limit: int = 10) -> Sequence[JobRecord]:
    """List the most recently created jobs.

    Args:
        session: SQLAlchemy Session instance.
        limit: Maximum number of jobs to return. Must be at least 1.

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


# ============================================================================
# Repository adapters
# ============================================================================


class SqlAlchemyMatchDecisionRepository:
    """SQLAlchemy implementation of MatchDecisionRepository protocol.

    This repository wraps the underlying SQLAlchemy session functions for
    match decision persistence, providing a clean interface for domain code.

    Attributes:
        session_factory: A SQLAlchemy sessionmaker that creates Session objects.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """Initialize the repository with a session factory.

        Args:
            session_factory: A SQLAlchemy sessionmaker for creating sessions.
        """
        self._session_factory = session_factory

    def upsert(self, job_id: str, decision: MatchDecision) -> MatchDecision:
        """Insert or update a match decision for a job.

        Args:
            job_id: The unique identifier for the job.
            decision: The MatchDecision instance to store.

        Returns:
            The stored MatchDecision instance.

        Raises:
            JobNotFoundError: If the job does not exist.
            IntegrityError: If the upsert violates constraints.
            ValueError: If decision is invalid.
        """
        # Validate inputs
        if not job_id:
            raise ValueError("job_id cannot be empty")
        if not decision.source_item_id:
            raise ValueError("decision.source_item_id cannot be empty")
        if not decision.reason:
            raise ValueError("decision.reason cannot be empty")

        with self._session_factory() as session:
            # Verify job exists
            job = session.query(JobRecord).filter_by(id=job_id).first()
            if job is None:
                raise JobNotFoundError(job_id)

            # Perform upsert
            try:
                record = upsert_match_decision(
                    session,
                    job_id,
                    decision.source_item_id,
                    decision,
                )
                # Return the domain model (the input decision is already a domain model)
                # We return it as-is since the decision contains the data we stored
                return decision
            except SQLAlchemyIntegrityError as e:
                session.rollback()
                raise IntegrityError(f"Integrity constraint violated: {e}") from e

    def unresolved(self, job_id: str) -> list[MatchDecision]:
        """List unresolved match decisions for a job.

        Returns decisions that are pending, matching, or in review.

        Args:
            job_id: The unique identifier for the job.

        Returns:
            A list of unresolved MatchDecision instances.
            Empty list if all decisions are resolved.

        Raises:
            JobNotFoundError: If the job does not exist.
        """
        if not job_id:
            raise ValueError("job_id cannot be empty")

        with self._session_factory() as session:
            # Verify job exists
            job = session.query(JobRecord).filter_by(id=job_id).first()
            if job is None:
                raise JobNotFoundError(job_id)

            # Get unresolved decisions (pending, matching, in_review)
            unresolved_statuses = ["pending", "matching", "in_review"]
            records = get_unresolved_decisions(
                session,
                job_id,
                status_filter=unresolved_statuses,
            )

            # Convert to domain models
            decisions = []
            for record in records:
                # Convert from database record to domain MatchDecision
                # We need to reconstruct the domain model from the stored data
                # The record has: source_item_id, spotify_track_id, score_json, decision_status, reviewed
                # Map decision_status to MatchDecision status
                if record.decision_status == "matched":
                    status = "matched"
                else:
                    status = "unmatched"

                # Reconstruct the SpotifyCandidate from the score_json if available
                selected_candidate = None
                score = None
                if record.spotify_track_id and record.score_json:
                    # Try to extract candidate info from score_json
                    # The score_json should contain track data
                    score_data = record.score_json
                    if "candidate" in score_data:
                        cand_data = score_data["candidate"]
                        selected_candidate = SpotifyCandidate(
                            track_id=cand_data.get("track_id", record.spotify_track_id),
                            uri=cand_data.get("uri", f"spotify:track:{record.spotify_track_id}"),
                            title=cand_data.get("title", ""),
                            artist_names=cand_data.get("artist_names", []),
                            album=cand_data.get("album", ""),
                            duration_seconds=cand_data.get("duration_seconds", 0),
                            explicit=cand_data.get("explicit", False),
                            isrc=cand_data.get("isrc"),
                            market_availability=cand_data.get("market_availability"),
                        )
                    # Reconstruct MatchScore from score_json
                    if "score_details" in score_data:
                        score_details = score_data["score_details"]
                        from playlist_bridge.domain.models import MatchScore
                        score = MatchScore(
                            overall=score_details.get("overall", 0.0),
                            title_similarity=score_details.get("title_similarity", 0.0),
                            artist_similarity=score_details.get("artist_similarity", 0.0),
                            duration_similarity=score_details.get("duration_similarity", 0.0),
                        )
                # For unmatched decisions, no selected_candidate or score
                if status == "unmatched":
                    selected_candidate = None
                    score = None

                decision = MatchDecision(
                    source_item_id=record.source_item_id,
                    status=status,
                    selected_candidate=selected_candidate,
                    ranked_alternatives=[],  # Not stored, we don't reconstruct alternatives currently
                    score=score,
                    reason=record.score_json.get("reason", "No reason provided") if record.score_json else "No reason provided",
                )
                decisions.append(decision)

            return decisions


class SqlAlchemyMatchCacheRepository:
    """SQLAlchemy implementation of MatchCacheRepository protocol.

    This repository wraps the underlying SQLAlchemy session functions for
    match cache persistence, providing a clean interface for domain code.

    Attributes:
        session_factory: A SQLAlchemy sessionmaker that creates Session objects.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """Initialize the repository with a session factory.

        Args:
            session_factory: A SQLAlchemy sessionmaker for creating sessions.
        """
        self._session_factory = session_factory

    def get(self, fingerprint: str) -> MatchCacheEntry | None:
        """Retrieve a match cache entry by fingerprint.

        Args:
            fingerprint: The source track fingerprint.

        Returns:
            The MatchCacheEntry instance, or None if not found.

        Raises:
            ValueError: If fingerprint is empty.
        """
        if not fingerprint:
            raise ValueError("fingerprint cannot be empty")

        with self._session_factory() as session:
            return lookup_match_cache(session, fingerprint)

    def upsert(self, entry: MatchCacheEntry) -> MatchCacheEntry:
        """Insert or update a match cache entry.

        Args:
            entry: The MatchCacheEntry instance to store.

        Returns:
            The stored MatchCacheEntry instance.

        Raises:
            IntegrityError: If the upsert violates constraints.
            ValueError: If entry is invalid.
        """
        if entry is None:
            raise ValueError("entry cannot be None")
        if not entry.source_fingerprint:
            raise ValueError("entry.source_fingerprint cannot be empty")
        if not entry.spotify_track_id:
            raise ValueError("entry.spotify_track_id cannot be empty")

        with self._session_factory() as session:
            try:
                result = upsert_match_cache(session, entry)
                return result
            except SQLAlchemyIntegrityError as e:
                session.rollback()
                raise IntegrityError(f"Integrity constraint violated: {e}") from e


class SqlAlchemyManualCorrectionRepository:
    """SQLAlchemy implementation of ManualCorrectionRepository protocol.

    This repository wraps the underlying SQLAlchemy session functions for
    manual correction persistence, providing a clean interface for domain code.

    Attributes:
        session_factory: A SQLAlchemy sessionmaker that creates Session objects.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        """Initialize the repository with a session factory.

        Args:
            session_factory: A SQLAlchemy sessionmaker for creating sessions.
        """
        self._session_factory = session_factory

    def get(self, fingerprint: str) -> ManualCorrection | None:
        """Retrieve a manual correction by fingerprint.

        Args:
            fingerprint: The source track fingerprint.

        Returns:
            The ManualCorrection instance, or None if not found.

        Raises:
            ValueError: If fingerprint is empty.
        """
        if not fingerprint:
            raise ValueError("fingerprint cannot be empty")

        with self._session_factory() as session:
            return lookup_manual_correction(session, fingerprint)

    def upsert(self, correction: ManualCorrection) -> ManualCorrection:
        """Insert or update a manual correction.

        Args:
            correction: The ManualCorrection instance to store.

        Returns:
            The stored ManualCorrection instance.

        Raises:
            IntegrityError: If the upsert violates constraints.
            ValueError: If correction is invalid.
        """
        if correction is None:
            raise ValueError("correction cannot be None")
        if not correction.source_fingerprint:
            raise ValueError("correction.source_fingerprint cannot be empty")
        # Either spotify_track_id or skip_reason must be provided, but not both
        if not correction.spotify_track_id and not correction.skip_reason:
            raise ValueError("correction must have either spotify_track_id or skip_reason")
        if correction.spotify_track_id and correction.skip_reason:
            raise ValueError("correction cannot have both spotify_track_id and skip_reason")

        with self._session_factory() as session:
            try:
                result = upsert_manual_correction(session, correction)
                return result
            except SQLAlchemyIntegrityError as e:
                session.rollback()
                raise IntegrityError(f"Integrity constraint violated: {e}") from e

