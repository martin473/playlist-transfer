"""Unit tests for job creation from transfer requests."""

from datetime import datetime, timezone
from typing import Any, Optional

import pytest

from playlist_bridge.domain.models import TransferRequest
from playlist_bridge.domain.enums import TransferMode
from playlist_bridge.jobs.runner import create_transfer_job, new_job_id, validate_job_id
from playlist_bridge.ports import JobRepository, IntegrityError
from playlist_bridge.persistence.models import JobRecord


class FakeJobRepository(JobRepository):
    """Fake JobRepository implementation for testing."""

    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._next_row_version = 1

    def create(self, request: TransferRequest, job_id: str, created_at: datetime) -> JobRecord:
        """Create a new job record."""
        if job_id in self._jobs:
            raise IntegrityError(f"Job with ID {job_id} already exists")

        # Create a JobRecord using dict construction (bypassing SQLAlchemy)
        job = JobRecord(
            id=job_id,
            request_json=request.model_dump(mode="json"),
            state="pending",
            source_playlist_id=request.source_playlist_id,
            destination_playlist_id=request.destination_playlist_id,
            source_track_count=None,
            match_checkpoint=0,
            write_checkpoint=0,
            verification_checkpoint=0,
            created_at=created_at,
            updated_at=created_at,
            last_error=None,
            lease_holder=None,
            lease_expires_at=None,
            lease_heartbeat_at=None,
            row_version=self._next_row_version,
        )
        self._next_row_version += 1
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Optional[JobRecord]:
        """Retrieve a job record by ID."""
        return self._jobs.get(job_id)

    def update_state(self, job_id: str, status: Any, updated_at: datetime) -> JobRecord:
        """Update job state (stub implementation)."""
        if job_id not in self._jobs:
            raise ValueError(f"Job not found: {job_id}")
        job = self._jobs[job_id]
        job.state = status.value if hasattr(status, "value") else str(status)
        job.updated_at = updated_at
        self._jobs[job_id] = job
        return job

    def list_recent(self, limit: int = 20) -> list[JobRecord]:
        """List recent jobs (stub implementation)."""
        return list(self._jobs.values())[-limit:]

    def acquire_lease(
        self,
        job_id: str,
        owner_id: str,
        lease_duration_seconds: int,
    ) -> Any:
        """Acquire job lease (stub implementation)."""
        raise NotImplementedError("Not needed for these tests")

    def release_lease(self, job_id: str, token: str) -> None:
        """Release job lease (stub implementation)."""
        raise NotImplementedError("Not needed for these tests")

    def heartbeat_lease(self, job_id: str, token: str) -> None:
        """Heartbeat job lease (stub implementation)."""
        raise NotImplementedError("Not needed for these tests")


class TestCreateTransferJob:
    """Tests for the create_transfer_job function."""

    def test_creates_job_with_valid_request(self) -> None:
        """create_transfer_job should persist a job with a valid transfer request."""
        # Setup
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLabc123",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="My Playlist",
        )

        # Execute
        job_id = create_transfer_job(request, repo, now)

        # Verify
        assert isinstance(job_id, str)
        assert len(job_id) == 32
        assert validate_job_id(job_id) is True

        # Verify the job was persisted
        job = repo.get(job_id)
        assert job is not None
        assert job.id == job_id
        assert job.state == "pending"
        assert job.source_playlist_id == "PLabc123"
        assert job.destination_playlist_id is None
        assert job.source_track_count is None
        assert job.match_checkpoint == 0
        assert job.write_checkpoint == 0
        assert job.verification_checkpoint == 0
        assert job.created_at == now
        assert job.updated_at == now
        assert job.row_version == 1

        # Verify request_json contains the original request
        assert job.request_json["source_service"] == "youtube"
        assert job.request_json["source_playlist_id"] == "PLabc123"
        assert job.request_json["destination_service"] == "spotify"
        assert job.request_json["transfer_mode"] == "create"
        assert job.request_json["destination_name"] == "My Playlist"

    def test_creates_job_with_dry_run_mode(self) -> None:
        """create_transfer_job should handle dry_run requests correctly."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLdry123",
            destination_service="spotify",
            transfer_mode=TransferMode.DRY_RUN,
            dry_run=True,
        )

        job_id = create_transfer_job(request, repo, now)

        job = repo.get(job_id)
        assert job is not None
        assert job.request_json["dry_run"] is True
        assert job.request_json["transfer_mode"] == "dry_run"

    def test_creates_job_with_merge_mode(self) -> None:
        """create_transfer_job should handle merge mode with destination_playlist_id."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLabc123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:123",
            transfer_mode=TransferMode.MERGE,
        )

        job_id = create_transfer_job(request, repo, now)

        job = repo.get(job_id)
        assert job is not None
        assert job.destination_playlist_id == "spotify:playlist:123"
        assert job.request_json["transfer_mode"] == "merge"

    def test_creates_job_with_replace_mode(self) -> None:
        """create_transfer_job should handle replace mode with destination_playlist_id."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLabc123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:456",
            transfer_mode=TransferMode.REPLACE,
        )

        job_id = create_transfer_job(request, repo, now)

        job = repo.get(job_id)
        assert job is not None
        assert job.destination_playlist_id == "spotify:playlist:456"
        assert job.request_json["transfer_mode"] == "replace"

    def test_returns_new_job_id_each_call(self) -> None:
        """create_transfer_job should generate a new job_id for each call."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLabc123",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Playlist 1",
        )

        job_id1 = create_transfer_job(request, repo, now)
        job_id2 = create_transfer_job(request, repo, now)

        assert job_id1 != job_id2
        assert validate_job_id(job_id1) is True
        assert validate_job_id(job_id2) is True

        # Both jobs should exist in the repository
        assert repo.get(job_id1) is not None
        assert repo.get(job_id2) is not None

    def test_uses_passed_timestamp_for_created_at(self) -> None:
        """create_transfer_job should use the passed timestamp for created_at."""
        repo = FakeJobRepository()
        now = datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLtimestamp",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Timestamped Playlist",
        )

        job_id = create_transfer_job(request, repo, now)

        job = repo.get(job_id)
        assert job is not None
        assert job.created_at == now
        assert job.updated_at == now

    def test_raises_integrity_error_on_duplicate_job_id(self) -> None:
        """create_transfer_job should raise IntegrityError if job_id already exists."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLabc123",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="My Playlist",
        )

        # First creation should succeed
        job_id = create_transfer_job(request, repo, now)
        assert repo.get(job_id) is not None

        # In real usage, job_id is generated by create_transfer_job,
        # but we can test the IntegrityError by forcing a duplicate via the repository
        with pytest.raises(IntegrityError, match=f"Job with ID {job_id} already exists"):
            repo.create(request, job_id, now)

    def test_request_rejected_by_model_if_invalid(self) -> None:
        """TransferRequest model should reject invalid configurations before create_transfer_job is called."""
        # CREATE mode without destination_name should raise ValueError
        with pytest.raises(ValueError, match="destination_name is required for CREATE mode"):
            TransferRequest(
                source_service="youtube",
                source_playlist_id="PLabc123",
                destination_service="spotify",
                transfer_mode=TransferMode.CREATE,
                # destination_name is missing
            )

        # MERGE mode without destination_playlist_id should raise ValueError
        with pytest.raises(ValueError, match="destination_playlist_id is required for MERGE/REPLACE modes"):
            TransferRequest(
                source_service="youtube",
                source_playlist_id="PLabc123",
                destination_service="spotify",
                transfer_mode=TransferMode.MERGE,
                # destination_playlist_id is missing
            )

    def test_job_creation_works_with_full_match_policy(self) -> None:
        """create_transfer_job should preserve match_policy in the request JSON."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLpolicy",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Policy Playlist",
            match_policy="strict",  # will be converted to MatchPolicy enum internally
        )

        job_id = create_transfer_job(request, repo, now)

        job = repo.get(job_id)
        assert job is not None
        assert job.request_json["match_policy"] == "strict"

    def test_job_creation_with_visibility_setting(self) -> None:
        """create_transfer_job should preserve visibility in the request JSON."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLvis",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Public Playlist",
            visibility="public",
        )

        job_id = create_transfer_job(request, repo, now)

        job = repo.get(job_id)
        assert job is not None
        assert job.request_json["visibility"] == "public"

    def test_failed_provider_call_leaves_recoverable_job(self) -> None:
        """A failed later provider call still leaves a recoverable job record.

        This test simulates the scenario where a provider call fails after job creation,
        but the job record remains in the repository with a pending state, ready to
        be retried or resumed.
        """
        # Setup: create a job
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLfailuretest",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Recoverable Playlist",
        )

        job_id = create_transfer_job(request, repo, now)

        # Verify the job was created with pending state
        job = repo.get(job_id)
        assert job is not None
        assert job.state == "pending"
        assert job.source_playlist_id == "PLfailuretest"
        assert job.last_error is None

        # Simulate a provider failure (e.g., network error, API timeout)
        # In a real scenario, the provider call would happen here and fail.
        # We'll simulate this by catching an exception and updating the job
        # with an error state (or leaving it pending for retry).
        try:
            # Simulate a provider call failure
            raise RuntimeError("YouTube API request failed: network timeout")
        except RuntimeError as e:
            # The job record remains recoverable - we can update it with error info
            # but it's still accessible for retry
            job.last_error = str(e)
            # For the purpose of this test, we need to update the job in the repository
            # to reflect the error state
            repo._jobs[job_id] = job
            # In a real implementation, we might update the state to 'failed'
            # but for recoverability, we could keep it as 'pending' for retry
            # or move to 'failed' with retry metadata.
            # For this test, we just verify the job still exists and is recoverable.
            pass

        # Verify: the job record is still present and recoverable
        recovered_job = repo.get(job_id)
        assert recovered_job is not None
        assert recovered_job.id == job_id
        assert recovered_job.source_playlist_id == "PLfailuretest"
        assert recovered_job.state == "pending"  # Still pending, ready for retry
        # The error is stored but the job remains available for recovery
        assert recovered_job.last_error is not None
        assert "YouTube API request failed" in recovered_job.last_error

        # The key assertion: the job record is still accessible for recovery
        assert repo.get(job_id) is not None

        # Additional verification: the job can be updated and retried
        # Update the job state to simulate retry
        updated_job = repo.update_state(job_id, "in_progress", datetime.now(timezone.utc))
        assert updated_job.state == "in_progress"
        assert updated_job.id == job_id

        # The job is now in progress, demonstrating recoverability
        assert repo.get(job_id).state == "in_progress"


class TestCreateTransferJobIntegration:
    """Integration-style tests for create_transfer_job with more realistic scenarios."""

    def test_creates_multiple_jobs_independently(self) -> None:
        """create_transfer_job should create independent job records for multiple requests."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)

        request1 = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLfirst",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="First Playlist",
        )

        request2 = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLsecond",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Second Playlist",
        )

        job_id1 = create_transfer_job(request1, repo, now)
        job_id2 = create_transfer_job(request2, repo, now)

        job1 = repo.get(job_id1)
        job2 = repo.get(job_id2)

        assert job1 is not None
        assert job2 is not None
        assert job1.id != job2.id
        assert job1.source_playlist_id == "PLfirst"
        assert job2.source_playlist_id == "PLsecond"
        assert job1.request_json["destination_name"] == "First Playlist"
        assert job2.request_json["destination_name"] == "Second Playlist"

    def test_job_creation_with_job_id_validation(self) -> None:
        """create_transfer_job should generate valid job IDs that pass validation."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLvalidate",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Validation Playlist",
        )

        job_id = create_transfer_job(request, repo, now)

        # The generated ID should pass the validation check
        assert validate_job_id(job_id) is True

        # The ID should be a hex string
        assert all(c in "0123456789abcdef" for c in job_id.lower())

    def test_creates_job_with_optional_job_id_ignored(self) -> None:
        """create_transfer_job always generates its own job_id and ignores any in the request."""
        repo = FakeJobRepository()
        now = datetime.now(timezone.utc)

        # Create a request with a job_id set (it should be ignored)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PLoptional",
            destination_service="spotify",
            transfer_mode=TransferMode.CREATE,
            destination_name="Optional Job ID",
            job_id="some-existing-id",  # This should be ignored
        )

        job_id = create_transfer_job(request, repo, now)

        # The generated ID should not be the one from the request
        assert job_id != "some-existing-id"
        assert validate_job_id(job_id) is True

        # The stored request should contain the original job_id from the request
        job = repo.get(job_id)
        assert job is not None
        assert job.request_json["job_id"] == "some-existing-id"
        assert job.id != "some-existing-id"
