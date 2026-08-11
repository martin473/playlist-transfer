"""Port interfaces for the playlist bridge.

This module defines service-neutral protocol interfaces that hide concrete
implementations (keyring, SQLAlchemy) from orchestration and CLI code.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Mapping, Protocol, Sequence, Union, runtime_checkable

from playlist_bridge.domain.enums import DestinationService, JobStatus, SourceService
from playlist_bridge.domain.models import (
    MatchDecision,
    MatchingConfig,
    SourceTrack,
    TransferRequest,
)
from playlist_bridge.persistence.models import (
    JobRecord,
    ManualCorrection,
    MatchCacheEntry,
)

if TYPE_CHECKING:
    from playlist_bridge.persistence.repositories import JobLease


# ============================================================================
# Error types
# ============================================================================


class CredentialCorruptionError(Exception):
    """Raised when stored credentials are malformed or cannot be deserialized.

    Attributes:
        service: The service name (e.g., "spotify", "youtube").
        profile_name: The profile name that was being accessed.
        safe_message: A human-readable message safe for logging/display.
    """

    def __init__(
        self,
        service: str,
        profile_name: str,
        safe_message: str,
    ) -> None:
        self.service = service
        self.profile_name = profile_name
        self.safe_message = safe_message
        super().__init__(f"Credential corruption for {service}/{profile_name}: {safe_message}")


class KeyringError(Exception):
    """Raised when the underlying keyring backend fails.

    This is a generic error for keyring read/write/delete failures.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class IntegrityError(Exception):
    """Raised when a database integrity constraint is violated.

    This is a domain-level error that wraps SQLAlchemy integrity errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


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


class ValueError(Exception):
    """Raised when a value is invalid.

    This is a domain-level error for invalid values.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


# ============================================================================
# Protocol: CredentialStore
# ============================================================================


@runtime_checkable
class CredentialStore(Protocol):
    """Service-neutral credential protocol.

    The CredentialStore hides the concrete keyring backend (e.g., macOS
    Keychain, Windows Credential Manager, libsecret) and provides typed
    save, load, and delete operations for OAuth tokens and other credentials.

    Implementations must:
        - Raise CredentialCorruptionError when stored data is malformed.
        - Raise KeyringError when the underlying keyring backend fails.
        - Never log or return raw credential secrets in error messages.
        - Store token_payload as a serializable mapping (dict[str, Any]).

    The service parameter must be a SourceService or DestinationService enum
    value. This allows the same store to be used for both source and
    destination authentication.
    """

    def save(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
        token_payload: Mapping[str, Any],
    ) -> None:
        """Save credentials for a given service and profile.

        Args:
            service: The service these credentials are for.
            profile_name: The profile name (e.g., "default", "work").
            token_payload: The credential data to store (e.g., OAuth token dict).

        Raises:
            CredentialCorruptionError: If token_payload cannot be serialized.
            KeyringError: If the keyring backend fails.
        """
        ...

    def load(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
    ) -> dict[str, Any] | None:
        """Load credentials for a given service and profile.

        Args:
            service: The service these credentials are for.
            profile_name: The profile name (e.g., "default", "work").

        Returns:
            The stored credential payload, or None if no credentials exist.

        Raises:
            CredentialCorruptionError: If the stored data is malformed.
            KeyringError: If the keyring backend fails.
        """
        ...

    def delete(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
    ) -> bool:
        """Delete credentials for a given service and profile.

        Args:
            service: The service these credentials are for.
            profile_name: The profile name (e.g., "default", "work").

        Returns:
            True if credentials were deleted, False if they did not exist.

        Raises:
            KeyringError: If the keyring backend fails.
        """
        ...


# ============================================================================
# Protocol: AccountProfileRepository
# ============================================================================

# Forward reference for AccountProfile (defined elsewhere)
# The protocol uses duck typing; the actual type is imported at runtime


@runtime_checkable
class AccountProfileRepository(Protocol):
    """Repository for AccountProfile persistence.

    The AccountProfileRepository hides the SQLAlchemy session and database
    implementation, providing typed save, get, and list operations over
    AccountProfile domain models.

    Implementations must:
        - Raise IntegrityError on constraint violations (e.g., duplicate profile).
        - Return None for get() when the profile does not exist.
        - Return fully populated AccountProfile domain objects.
        - Support filtering by service when listing.

    The service parameter may be None to list all profiles across all services.
    """

    def save(self, profile: Any) -> Any:
        """Save an AccountProfile to the repository.

        Args:
            profile: The AccountProfile instance to save.

        Returns:
            The saved AccountProfile instance (may include generated fields).

        Raises:
            IntegrityError: If a constraint violation occurs.
        """
        ...

    def get(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
    ) -> Any | None:
        """Retrieve an AccountProfile by service and profile name.

        Args:
            service: The service the profile is for.
            profile_name: The profile name (e.g., "default", "work").

        Returns:
            The AccountProfile instance, or None if not found.
        """
        ...

    def list(
        self,
        service: Union[SourceService, DestinationService, None] = None,
    ) -> list[Any]:
        """List AccountProfiles, optionally filtered by service.

        Args:
            service: If provided, only list profiles for this service.
                    If None, list all profiles across all services.

        Returns:
            A list of AccountProfile instances (empty list if none).
        """
        ...


# ============================================================================
# Protocol: JobRepository
# ============================================================================


@runtime_checkable
class JobRepository(Protocol):
    """Repository for JobRecord persistence and lease management.

    The JobRepository hides the SQLAlchemy session and database implementation,
    providing typed operations over JobRecord domain models with lease support
    for distributed job processing.

    Implementations must:
        - Raise JobNotFoundError when a job ID does not exist.
        - Raise JobLeaseBusyError when a lease is held by another owner.
        - Raise LeaseLostError when a lease is lost (stale takeover).
        - Raise IntegrityError on constraint violations.
        - Raise ValueError for invalid parameters.
        - Use secure random token generation for lease tokens.
        - Implement compare-and-swap semantics for lease acquisition.
    """

    def create(
        self,
        request: TransferRequest,
        job_id: str,
        created_at: datetime,
    ) -> JobRecord:
        """Create a new job record from a transfer request.

        Args:
            request: The transfer request containing source/destination details.
            job_id: The unique identifier for the job.
            created_at: The timestamp when the job was created.

        Returns:
            The created JobRecord instance.

        Raises:
            IntegrityError: If a job with the same ID already exists.
            ValueError: If the request or job_id is invalid.
        """
        ...

    def get(self, job_id: str) -> JobRecord | None:
        """Retrieve a job record by ID.

        Args:
            job_id: The unique identifier for the job.

        Returns:
            The JobRecord instance, or None if not found.
        """
        ...

    def update_state(
        self,
        job_id: str,
        status: JobStatus,
        updated_at: datetime,
    ) -> JobRecord:
        """Update the state of a job.

        Args:
            job_id: The unique identifier for the job.
            status: The new job status.
            updated_at: The timestamp of the update.

        Returns:
            The updated JobRecord instance.

        Raises:
            JobNotFoundError: If the job does not exist.
            IntegrityError: If the update violates constraints.
            ValueError: If the status transition is invalid.
        """
        ...

    def update_checkpoint(
        self,
        job_id: str,
        checkpoint_fields: Mapping[str, Any],
        updated_at: datetime,
        *,
        lease: JobLease,
    ) -> JobRecord:
        """Update checkpoint fields for a job with lease validation.

        Args:
            job_id: The unique identifier for the job.
            checkpoint_fields: Mapping of checkpoint field names to values.
            updated_at: The timestamp of the update.
            lease: The current JobLease object for compare-and-swap validation.

        Returns:
            The updated JobRecord instance.

        Raises:
            JobNotFoundError: If the job does not exist.
            LeaseLostError: If the lease token or row version does not match.
            IntegrityError: If the update violates constraints.
            ValueError: If checkpoint_fields is invalid.
        """
        ...

    def record_error(
        self,
        job_id: str,
        safe_code: str,
        safe_message: str,
        updated_at: datetime,
    ) -> JobRecord:
        """Record an error on a job.

        Args:
            job_id: The unique identifier for the job.
            safe_code: A safe error code (not containing secrets).
            safe_message: A safe error message (not containing secrets).
            updated_at: The timestamp of the error.

        Returns:
            The updated JobRecord instance.

        Raises:
            JobNotFoundError: If the job does not exist.
            IntegrityError: If the update violates constraints.
            ValueError: If the error message contains sensitive data.
        """
        ...

    def list_recent(self, limit: int = 20) -> list[JobRecord]:
        """List the most recent jobs.

        Args:
            limit: Maximum number of jobs to return (default: 20).

        Returns:
            A list of JobRecord instances in descending order of creation.
            Empty list if no jobs exist.

        Raises:
            ValueError: If limit is less than 1.
        """
        ...

    def acquire_lease(
        self,
        job_id: str,
        owner_id: str,
        now: datetime,
        lease_duration: timedelta,
        current_token: str | None = None,
    ) -> JobLease:
        """Acquire a lease on a job.

        Args:
            job_id: The unique identifier for the job.
            owner_id: The identifier of the lease holder (e.g., process ID).
            now: The current timestamp for lease acquisition.
            lease_duration: The duration for which the lease is valid.
            current_token: The current token for reentrant acquisition.

        Returns:
            A JobLease instance containing the lease details.

        Raises:
            JobNotFoundError: If the job does not exist.
            JobLeaseBusyError: If the lease is held by a different owner.
            IntegrityError: If the acquisition violates constraints.
            ValueError: If owner_id is empty.
        """
        ...

    def heartbeat_lease(
        self,
        lease: JobLease,
        now: datetime,
        lease_duration: timedelta,
    ) -> JobLease:
        """Extend the expiration of an active lease.

        Args:
            lease: The current JobLease object containing the lease details.
            now: The current timestamp for heartbeat update.
            lease_duration: The new duration for the lease.

        Returns:
            An updated JobLease instance with the new expiration time,
            heartbeat timestamp, and row version.

        Raises:
            JobNotFoundError: If the job does not exist.
            LeaseLostError: If the lease token or row version does not match.
            IntegrityError: If the update violates constraints.
        """
        ...

    def release_lease(self, lease: JobLease, now: datetime) -> bool:
        """Release an active lease.

        Args:
            lease: JobLease instance containing lease holder, token, expiration,
                   row version, and heartbeat.
            now: The current timestamp for lease release.

        Returns:
            True if the lease was successfully released, False if the lease
            was already expired or the token did not match.

        Raises:
            JobNotFoundError: If the job does not exist.
            LeaseLostError: If the lease token or row version does not match.
            IntegrityError: If the release violates constraints.
        """
        ...


# ============================================================================
# Protocol: SourceTrackRepository
# ============================================================================


@runtime_checkable
class SourceTrackRepository(Protocol):
    """Repository for SourceTrack persistence.

    The SourceTrackRepository hides the SQLAlchemy session and database
    implementation, providing typed operations over SourceTrack domain models.

    Implementations must:
        - Raise JobNotFoundError when a job ID does not exist.
        - Raise IntegrityError on constraint violations.
        - Return empty lists for jobs with no tracks.
        - Preserve track order when returning lists.
    """

    def replace_for_job(
        self,
        job_id: str,
        tracks: Sequence[SourceTrack],
    ) -> int:
        """Replace all tracks for a job with a new sequence.

        Args:
            job_id: The unique identifier for the job.
            tracks: The sequence of SourceTrack instances to store.

        Returns:
            The number of tracks inserted.

        Raises:
            JobNotFoundError: If the job does not exist.
            IntegrityError: If the replacement violates constraints.
            ValueError: If tracks is empty or contains invalid data.
        """
        ...

    def list_ordered(self, job_id: str) -> list[SourceTrack]:
        """List all tracks for a job in ascending position order.

        Args:
            job_id: The unique identifier for the job.

        Returns:
            A list of SourceTrack instances in ascending position order.
            Empty list if no tracks exist.

        Raises:
            JobNotFoundError: If the job does not exist.
        """
        ...

    def get(self, job_id: str, source_item_id: str) -> SourceTrack | None:
        """Retrieve a specific track by job ID and source item ID.

        Args:
            job_id: The unique identifier for the job.
            source_item_id: The source item identifier.

        Returns:
            The SourceTrack instance, or None if not found.

        Raises:
            JobNotFoundError: If the job does not exist.
            ValueError: If source_item_id is empty.
        """
        ...


# ============================================================================
# Protocol: MatchDecisionRepository
# ============================================================================


@runtime_checkable
class MatchDecisionRepository(Protocol):
    """Repository for MatchDecision persistence.

    The MatchDecisionRepository hides the SQLAlchemy session and database
    implementation, providing typed operations over MatchDecision domain models.

    Implementations must:
        - Raise JobNotFoundError when a job ID does not exist.
        - Raise IntegrityError on constraint violations.
        - Return empty lists for jobs with no decisions.
        - Support atomic upsert operations.
    """

    def upsert(
        self,
        job_id: str,
        decision: MatchDecision,
    ) -> MatchDecision:
        """Insert or update a match decision for a job.

        Args:
            job_id: The unique identifier for the job.
            decision: The MatchDecision instance to store.

        Returns:
            The stored MatchDecision instance (may include generated fields).

        Raises:
            JobNotFoundError: If the job does not exist.
            IntegrityError: If the upsert violates constraints.
            ValueError: If decision is invalid.
        """
        ...

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
        ...


# ============================================================================
# Protocol: MatchCacheRepository
# ============================================================================


@runtime_checkable
class MatchCacheRepository(Protocol):
    """Repository for MatchCacheEntry persistence.

    The MatchCacheRepository hides the SQLAlchemy session and database
    implementation, providing typed operations over MatchCacheEntry domain models.

    Implementations must:
        - Raise IntegrityError on constraint violations.
        - Return None for get() when the fingerprint does not exist.
        - Support atomic upsert operations.
    """

    def get(self, fingerprint: str) -> MatchCacheEntry | None:
        """Retrieve a match cache entry by fingerprint.

        Args:
            fingerprint: The source track fingerprint.

        Returns:
            The MatchCacheEntry instance, or None if not found.

        Raises:
            ValueError: If fingerprint is empty.
        """
        ...

    def upsert(self, entry: MatchCacheEntry) -> MatchCacheEntry:
        """Insert or update a match cache entry.

        Args:
            entry: The MatchCacheEntry instance to store.

        Returns:
            The stored MatchCacheEntry instance (may include generated fields).

        Raises:
            IntegrityError: If the upsert violates constraints.
            ValueError: If entry is invalid.
        """
        ...


# ============================================================================
# Protocol: ManualCorrectionRepository
# ============================================================================


@runtime_checkable
class ManualCorrectionRepository(Protocol):
    """Repository for ManualCorrection persistence.

    The ManualCorrectionRepository hides the SQLAlchemy session and database
    implementation, providing typed operations over ManualCorrection domain models.

    Implementations must:
        - Raise IntegrityError on constraint violations.
        - Return None for get() when the fingerprint does not exist.
        - Support atomic upsert operations.
        - Store either spotify_track_id or skip_reason, not both.
    """

    def get(self, fingerprint: str) -> ManualCorrection | None:
        """Retrieve a manual correction by fingerprint.

        Args:
            fingerprint: The source track fingerprint.

        Returns:
            The ManualCorrection instance, or None if not found.

        Raises:
            ValueError: If fingerprint is empty.
        """
        ...

    def upsert(self, correction: ManualCorrection) -> ManualCorrection:
        """Insert or update a manual correction.

        Args:
            correction: The ManualCorrection instance to store.

        Returns:
            The stored ManualCorrection instance (may include generated fields).

        Raises:
            IntegrityError: If the upsert violates constraints.
            ValueError: If correction is invalid.
        """
        ...


# ============================================================================
# Type aliases for supporting dependency contracts
# ============================================================================

# Clock: A callable that returns the current datetime.
Clock = Callable[[], datetime]

# ReportPathFactory: A callable that creates a Path for a report file.
ReportPathFactory = Callable[[str, str], Path]


# ============================================================================
# Dependency container classes
# ============================================================================


class RunnerRepositories:
    """Dependency container for the runner layer.

    Aggregates the repositories needed by the runner orchestration layer.

    Attributes:
        jobs: JobRepository instance for job persistence and leases.
        tracks: SourceTrackRepository instance for source track persistence.
        decisions: MatchDecisionRepository instance for match decision persistence.
    """

    def __init__(
        self,
        jobs: JobRepository,
        tracks: SourceTrackRepository,
        decisions: MatchDecisionRepository,
    ) -> None:
        """Initialize the runner repositories container.

        Args:
            jobs: JobRepository instance for job persistence and leases.
            tracks: SourceTrackRepository instance for source track persistence.
            decisions: MatchDecisionRepository instance for match decision persistence.

        Raises:
            ValueError: If any of the repository arguments are None.
        """
        if jobs is None:
            raise ValueError("jobs repository cannot be None")
        if tracks is None:
            raise ValueError("tracks repository cannot be None")
        if decisions is None:
            raise ValueError("decisions repository cannot be None")
        self.jobs = jobs
        self.tracks = tracks
        self.decisions = decisions


class ReviewRepositories:
    """Dependency container for the review layer.

    Aggregates the repositories needed by the review orchestration layer.

    Attributes:
        jobs: JobRepository instance for job persistence and leases.
        tracks: SourceTrackRepository instance for source track persistence.
        decisions: MatchDecisionRepository instance for match decision persistence.
        corrections: ManualCorrectionRepository instance for correction persistence.
    """

    def __init__(
        self,
        jobs: JobRepository,
        tracks: SourceTrackRepository,
        decisions: MatchDecisionRepository,
        corrections: ManualCorrectionRepository,
    ) -> None:
        """Initialize the review repositories container.

        Args:
            jobs: JobRepository instance for job persistence and leases.
            tracks: SourceTrackRepository instance for source track persistence.
            decisions: MatchDecisionRepository instance for match decision persistence.
            corrections: ManualCorrectionRepository instance for correction persistence.

        Raises:
            ValueError: If any of the repository arguments are None.
        """
        if jobs is None:
            raise ValueError("jobs repository cannot be None")
        if tracks is None:
            raise ValueError("tracks repository cannot be None")
        if decisions is None:
            raise ValueError("decisions repository cannot be None")
        if corrections is None:
            raise ValueError("corrections repository cannot be None")
        self.jobs = jobs
        self.tracks = tracks
        self.decisions = decisions
        self.corrections = corrections


class MatcherDependencies:
    """Dependency container for the matching layer.

    Aggregates the dependencies needed by the matching orchestration layer.

    Attributes:
        spotify: SpotifyAdapter instance for search operations.
        decisions: MatchDecisionRepository instance for decision persistence.
        match_cache: MatchCacheRepository instance for match cache operations.
        corrections: ManualCorrectionRepository instance for correction lookups.
        matching_config: MatchingConfig instance containing matching parameters.
        clock: Clock callable for timestamp generation.
    """

    def __init__(
        self,
        spotify: Any,  # SpotifyAdapter protocol would be imported here
        decisions: MatchDecisionRepository,
        match_cache: MatchCacheRepository,
        corrections: ManualCorrectionRepository,
        matching_config: MatchingConfig,
        clock: Clock,
    ) -> None:
        """Initialize the matcher dependencies container.

        Args:
            spotify: SpotifyAdapter instance for search operations.
            decisions: MatchDecisionRepository instance for decision persistence.
            match_cache: MatchCacheRepository instance for match cache operations.
            corrections: ManualCorrectionRepository instance for correction lookups.
            matching_config: MatchingConfig instance containing matching parameters.
            clock: Clock callable for timestamp generation.

        Raises:
            ValueError: If any of the dependency arguments are None.
        """
        if spotify is None:
            raise ValueError("spotify adapter cannot be None")
        if decisions is None:
            raise ValueError("decisions repository cannot be None")
        if match_cache is None:
            raise ValueError("match_cache repository cannot be None")
        if corrections is None:
            raise ValueError("corrections repository cannot be None")
        if matching_config is None:
            raise ValueError("matching_config cannot be None")
        if clock is None:
            raise ValueError("clock cannot be None")
        self.spotify = spotify
        self.decisions = decisions
        self.match_cache = match_cache
        self.corrections = corrections
        self.matching_config = matching_config
        self.clock = clock
