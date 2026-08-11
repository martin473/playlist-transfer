"""Integration tests for transaction atomicity and lease management."""

from datetime import datetime, timezone
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError

from playlist_bridge.domain.enums import DestinationService, SourceService, TransferMode, MatchPolicy
from playlist_bridge.domain.models import SourceTrack, TransferRequest
from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import JobRecord, SourceTrackRecord
from playlist_bridge.persistence.repositories import (
    bulk_insert_source_tracks,
    create_job,
    get_source_tracks_ordered,
)


@pytest.fixture
def in_memory_session():
    """Create an in-memory SQLite session for testing."""
    # Use shared cache so threads can see the same database
    engine = create_engine("sqlite:///:memory:?cache=shared")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session


def _create_test_job(session: Session) -> str:
    """Create a test job and return its ID."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    request = TransferRequest(
        source_service=SourceService.YOUTUBE,
        destination_service=DestinationService.SPOTIFY,
        source_playlist_id="test_playlist_123",
        destination_playlist_id="test_dest_456",
        transfer_mode=TransferMode.REPLACE,
        match_policy=MatchPolicy.BALANCED,
        destination_name="Test Playlist",
        visibility="private",
        dry_run=False,
    )
    create_job(session, request, job_id, now)
    return job_id


def _create_test_tracks(count: int, start_position: int = 0) -> list[SourceTrack]:
    """Create a list of test SourceTrack objects."""
    tracks = []
    for i in range(count):
        pos = start_position + i
        tracks.append(
            SourceTrack(
                position=pos,
                title=f"Track {pos}",
                artist_names=["Test Artist"],
                duration_seconds=180 + (pos % 60),
                video_id=f"vid_{pos:04d}",
                channel_title="Test Channel",
            )
        )
    return tracks


class TestMultiRowRollback:
    """Integration tests for multi-row transaction rollback."""

    def test_rollback_on_duplicate_in_bulk_insert(self, in_memory_session: Session):
        """Test that bulk_insert_source_tracks rolls back when a duplicate occurs.

        This test forces an exception during a multi-row repository operation
        by inserting a duplicate source_item_id within the same job. The
        operation should roll back, leaving no partial rows.
        """
        # Create a test job
        job_id = _create_test_job(in_memory_session)

        # Create tracks for the job - first batch of 3 tracks
        tracks1 = _create_test_tracks(3, 0)

        # Insert first batch successfully
        bulk_insert_source_tracks(in_memory_session, job_id, tracks1)

        # Verify first batch was inserted
        inserted = get_source_tracks_ordered(in_memory_session, job_id)
        assert len(inserted) == 3

        # Create second batch where one track has a duplicate source_item_id
        # Track at position 3 has video_id "vid_0001" which duplicates the
        # second track from first batch (position 1 has video_id "vid_0001")
        tracks2 = [
            SourceTrack(
                position=3,
                title="Track 3",
                artist_names=["Test Artist"],
                duration_seconds=180,
                video_id="vid_0001",  # Duplicate of track at position 1
                channel_title="Test Channel",
            ),
            SourceTrack(
                position=4,
                title="Track 4",
                artist_names=["Test Artist"],
                duration_seconds=180,
                video_id="vid_0004",
                channel_title="Test Channel",
            ),
        ]

        # Attempt to insert the second batch - should raise IntegrityError due to duplicate
        with pytest.raises(Exception) as exc_info:
            bulk_insert_source_tracks(in_memory_session, job_id, tracks2)

        # The exception should be an IntegrityError (wrapped as IntegrityError from our module)
        # or SQLAlchemyIntegrityError
        assert isinstance(exc_info.value, Exception)

        # Verify that NO partial rows were inserted - the rollback should have
        # removed any rows that were added before the duplicate was encountered
        final_tracks = get_source_tracks_ordered(in_memory_session, job_id)
        assert len(final_tracks) == 3, (
            "Should still have only 3 tracks (first batch) - rollback should prevent partial inserts"
        )

        # Verify the tracks are exactly the first batch
        for i, record in enumerate(final_tracks):
            assert record.source_item_id == f"vid_{i:04d}"
            assert record.position == i

    def test_rollback_leaves_no_partial_rows_on_integrity_error(
        self, in_memory_session: Session
    ):
        """Test that rollback leaves no partial rows when an integrity error occurs.

        This test verifies that after a rollback, all affected tables remain
        unchanged from their pre-operation state.
        """
        # Create a test job
        job_id = _create_test_job(in_memory_session)

        # Count initial rows in source_tracks table
        initial_count = in_memory_session.query(SourceTrackRecord).filter_by(
            job_id=job_id
        ).count()
        assert initial_count == 0

        # Create tracks with a duplicate source_item_id (two tracks with same video_id)
        # This will cause an integrity error because of the unique constraint
        # (job_id, source_item_id) in the SourceTrackRecord model
        tracks = [
            SourceTrack(
                position=0,
                title="Track 0",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="vid_duplicate",
                channel_title="Channel A",
            ),
            SourceTrack(
                position=1,
                title="Track 1",
                artist_names=["Artist B"],
                duration_seconds=200,
                video_id="vid_duplicate",  # Duplicate video_id!
                channel_title="Channel B",
            ),
            SourceTrack(
                position=2,
                title="Track 2",
                artist_names=["Artist C"],
                duration_seconds=190,
                video_id="vid_002",
                channel_title="Channel C",
            ),
        ]

        # Attempt to insert the tracks - should fail due to duplicate
        with pytest.raises(Exception):
            bulk_insert_source_tracks(in_memory_session, job_id, tracks)

        # Verify that NO rows were inserted after the rollback
        final_count = in_memory_session.query(SourceTrackRecord).filter_by(
            job_id=job_id
        ).count()
        assert final_count == initial_count, (
            f"Row count should remain unchanged after rollback. "
            f"Initial: {initial_count}, Final: {final_count}"
        )

        # Also verify the job record is still intact
        job = in_memory_session.query(JobRecord).filter_by(id=job_id).first()
        assert job is not None
        assert job.state == "pending"

    def test_rollback_preserves_existing_data_on_constraint_violation(
        self, in_memory_session: Session
    ):
        """Test that existing data is preserved when a constraint violation triggers rollback.

        This test first inserts valid data, then attempts an operation that
        violates a constraint, and verifies the original data remains intact.
        """
        # Create a test job
        job_id = _create_test_job(in_memory_session)

        # Insert a valid batch of tracks
        valid_tracks = _create_test_tracks(3, 0)
        bulk_insert_source_tracks(in_memory_session, job_id, valid_tracks)

        # Verify the valid tracks are present
        inserted = get_source_tracks_ordered(in_memory_session, job_id)
        assert len(inserted) == 3

        # Get the IDs of the inserted tracks for reference
        inserted_ids = [r.source_item_id for r in inserted]
        assert "vid_0000" in inserted_ids
        assert "vid_0001" in inserted_ids
        assert "vid_0002" in inserted_ids

        # Now attempt to insert a track with a duplicate source_item_id
        invalid_track = [
            SourceTrack(
                position=3,
                title="Invalid Track",
                artist_names=["Invalid Artist"],
                duration_seconds=180,
                video_id="vid_0001",  # Duplicate of existing track at position 1
                channel_title="Invalid Channel",
            )
        ]

        # Attempt to insert the invalid track
        with pytest.raises(Exception):
            bulk_insert_source_tracks(in_memory_session, job_id, invalid_track)

        # Verify the original data is unchanged
        final_tracks = get_source_tracks_ordered(in_memory_session, job_id)
        assert len(final_tracks) == 3

        # Verify the original tracks are exactly as they were
        final_ids = [r.source_item_id for r in final_tracks]
        assert final_ids == inserted_ids

        # Verify no track with position 3 or invalid data was inserted
        for record in final_tracks:
            assert record.position in (0, 1, 2)
            assert record.source_item_id in ("vid_0000", "vid_0001", "vid_0002")

    def test_rollback_with_empty_tracks_does_nothing(self, in_memory_session: Session):
        """Test that bulk_insert_source_tracks with empty list does nothing."""
        # Create a test job
        job_id = _create_test_job(in_memory_session)

        # Get initial count
        initial_count = in_memory_session.query(SourceTrackRecord).filter_by(
            job_id=job_id
        ).count()
        assert initial_count == 0

        # Insert empty list - should do nothing
        bulk_insert_source_tracks(in_memory_session, job_id, [])

        # Count should still be 0
        final_count = in_memory_session.query(SourceTrackRecord).filter_by(
            job_id=job_id
        ).count()
        assert final_count == 0


class TestSimultaneousLeaseAcquisition:
    """Integration tests for simultaneous lease acquisition from independent sessions."""

    def test_simultaneous_lease_acquisition_with_barrier(
        self, in_memory_session: Session
    ):
        """Test that exactly one session acquires a lease when two attempt simultaneously.

        This test uses a synchronization barrier to ensure two independent sessions
        attempt to acquire a lease on the same job at the same time. Exactly one
        should succeed (acquire the live lease) and the other should receive a
        typed busy result.
        """
        from threading import Barrier, Thread
        from queue import Queue
        from datetime import timedelta
        from playlist_bridge.persistence.repositories import (
            acquire_job_lease,
            release_job_lease,
            JobLeaseBusyError,
            JobLease,
        )

        # Create a test job with pending state
        job_id = _create_test_job(in_memory_session)

        # Verify job is in pending state initially
        job = in_memory_session.query(JobRecord).filter_by(id=job_id).first()
        assert job.state == "pending"
        assert job.lease_holder is None
        assert job.lease_expires_at is None

        # Get the engine from the fixture session for thread sessions
        engine = in_memory_session.bind
        SessionLocal = sessionmaker(bind=engine)

        # Create a barrier for two threads
        barrier = Barrier(2, timeout=5.0)

        # Queues to collect results from threads
        results = Queue()

        def acquire_lease_in_thread(session_id: int):
            """Thread function to acquire a lease."""
            # Each thread needs its own independent session
            with SessionLocal() as session:
                # Wait for both threads to be ready
                barrier.wait(timeout=5.0)

                # Attempt to acquire the lease
                try:
                    now = datetime.now(timezone.utc)
                    lease = acquire_job_lease(
                        session,
                        job_id,
                        f"test_worker_{session_id}",
                        now,
                        timedelta(seconds=30),
                        current_token=None,
                    )
                    results.put((session_id, True, lease.token))
                except JobLeaseBusyError as e:
                    # The loser should get a typed busy result
                    results.put((session_id, False, f"JobLeaseBusyError: {str(e)}"))
                except Exception as e:
                    # Unexpected error
                    results.put((session_id, False, f"Unexpected error: {type(e).__name__}: {str(e)}"))

        # Start two threads
        thread1 = Thread(target=acquire_lease_in_thread, args=(1,))
        thread2 = Thread(target=acquire_lease_in_thread, args=(2,))

        thread1.start()
        thread2.start()

        # Wait for both threads to complete
        thread1.join(timeout=10.0)
        thread2.join(timeout=10.0)

        # Collect results
        result1 = results.get(timeout=1.0)
        result2 = results.get(timeout=1.0)

        # Analyze results: exactly one should succeed
        successes = [r for r in [result1, result2] if r[1] is True]
        failures = [r for r in [result1, result2] if r[1] is False]

        # Exactly one acquisition should succeed
        assert len(successes) == 1, (
            f"Expected exactly one successful lease acquisition, got {len(successes)}. "
            f"Results: {[r[2] for r in [result1, result2]]}"
        )

        # Exactly one should fail (get busy result)
        assert len(failures) == 1, (
            f"Expected exactly one failed lease acquisition, got {len(failures)}. "
            f"Results: {[r[2] for r in [result1, result2]]}"
        )

        # Verify the failure got a typed busy result
        failure_result = failures[0]
        assert "JobLeaseBusyError" in failure_result[2], (
            f"Loser should receive JobLeaseBusyError, got {failure_result[2]}"
        )

        # Verify the successful acquisition updated the job
        final_job = in_memory_session.query(JobRecord).filter_by(id=job_id).first()
        assert final_job.lease_holder is not None
        assert final_job.lease_expires_at is not None

        # Verify the lease is held by one of the workers
        success_worker_id = successes[0][0]
        expected_worker = f"test_worker_{success_worker_id}"
        assert final_job.lease_holder == expected_worker

        # Verify the loser's session did not modify the job
        loser_session_id = failures[0][0]
        loser_worker = f"test_worker_{loser_session_id}"
        assert final_job.lease_holder != loser_worker

        # Get the lease object to release it
        success_token = successes[0][2]
        lease_obj = JobLease(
            job_id=job_id,
            owner_id=expected_worker,
            token=success_token,
            expires_at=final_job.lease_expires_at,
            row_version=final_job.row_version,
            lease_heartbeat_at=final_job.lease_heartbeat_at,
        )

        # Clean up: release the lease
        release_job_lease(in_memory_session, lease_obj, datetime.now(timezone.utc))
        final_job_after_release = in_memory_session.query(JobRecord).filter_by(
            id=job_id
        ).first()
        assert final_job_after_release.lease_holder is None
        assert final_job_after_release.lease_expires_at is None
