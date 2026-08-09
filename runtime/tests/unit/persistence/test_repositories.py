"""Unit tests for repository functions."""

from datetime import datetime, timezone
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from playlist_bridge.domain.enums import TransferMode
from playlist_bridge.domain.models import SourceTrack, TransferRequest
from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import JobRecord, MatchCacheEntry
from playlist_bridge.persistence.repositories import (
    JobNotFoundError,
    bulk_insert_source_tracks,
    create_job,
    lookup_match_cache,
)


@pytest.fixture
def in_memory_session():
    """Create an in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as session:
        yield session


class TestLookupMatchCache:
    """Tests for lookup_match_cache function."""

    def test_missing_fingerprint_returns_none(self, in_memory_session: Session):
        """A missing fingerprint returns no entry."""
        result = lookup_match_cache(in_memory_session, "non-existent-fingerprint")
        assert result is None

    def test_existing_fingerprint_returns_entry(self, in_memory_session: Session):
        """An existing fingerprint returns the matching entry."""
        # Insert a cache entry
        entry = MatchCacheEntry(
            source_fingerprint="test-fingerprint-123",
            spotify_track_id="spotify:track:abc123",
            confidence=85,
            origin="manual",
            last_verified_at=datetime.now(),
        )
        in_memory_session.add(entry)
        in_memory_session.commit()

        # Look it up
        result = lookup_match_cache(in_memory_session, "test-fingerprint-123")
        assert result is not None
        assert result.source_fingerprint == "test-fingerprint-123"
        assert result.spotify_track_id == "spotify:track:abc123"
        assert result.confidence == 85
        assert result.origin == "manual"

    def test_wrong_fingerprint_returns_none(self, in_memory_session: Session):
        """A fingerprint that doesn't match any entry returns None."""
        # Insert a cache entry with a specific fingerprint
        entry = MatchCacheEntry(
            source_fingerprint="existing-fingerprint-456",
            spotify_track_id="spotify:track:xyz789",
            confidence=70,
            origin="auto",
            last_verified_at=datetime.now(),
        )
        in_memory_session.add(entry)
        in_memory_session.commit()

        # Look up a different fingerprint
        result = lookup_match_cache(in_memory_session, "different-fingerprint-456")
        assert result is None


class TestCreateJob:
    """Tests for create_job function."""

    def test_create_job_success(self, in_memory_session: Session):
        """Creating a job with valid data should persist and reload correctly."""
        # Create a transfer request
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PL123456789",
            destination_service="spotify",
            destination_name="My New Playlist",
            transfer_mode=TransferMode.CREATE,
            match_policy="balanced",
            visibility="private",
            dry_run=False,
        )

        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)

        # Create the job
        job = create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)

        # Verify the job was created correctly
        assert job.id == job_id
        assert job.state == "pending"
        assert job.source_playlist_id == "PL123456789"
        assert job.destination_playlist_id is None  # Not set for CREATE mode
        assert job.source_track_count is None
        assert job.match_checkpoint == 0
        assert job.write_checkpoint == 0
        assert job.verification_checkpoint == 0
        # SQLite does not store timezone info, so compare normalized UTC values
        assert job.created_at.replace(tzinfo=timezone.utc) == created_at
        assert job.updated_at.replace(tzinfo=timezone.utc) == created_at
        assert job.last_error is None
        assert job.lease_holder is None
        assert job.lease_expires_at is None
        assert job.lease_heartbeat_at is None
        assert job.row_version == 1

        # Verify the request_json was stored correctly
        assert job.request_json["source_service"] == "youtube"
        assert job.request_json["source_playlist_id"] == "PL123456789"
        assert job.request_json["destination_service"] == "spotify"
        assert job.request_json["destination_name"] == "My New Playlist"
        assert job.request_json["transfer_mode"] == "create"

        # Reload the job from the database and verify it can be retrieved
        reloaded = in_memory_session.query(JobRecord).filter_by(id=job_id).first()
        assert reloaded is not None
        assert reloaded.id == job_id
        assert reloaded.state == "pending"
        assert reloaded.request_json == job.request_json

    def test_create_job_duplicate_id_raises_integrity_error(self, in_memory_session: Session):
        """Creating a job with an existing ID should raise IntegrityError."""
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PL123456789",
            destination_service="spotify",
            destination_name="My Playlist",
            transfer_mode=TransferMode.CREATE,
        )

        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)

        # Create the first job
        create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)

        # Attempt to create a second job with the same ID
        with pytest.raises(IntegrityError):
            create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)


class TestBulkInsertSourceTracks:
    """Tests for bulk_insert_source_tracks function."""

    def test_bulk_insert_success(self, in_memory_session: Session):
        """Bulk inserting tracks for an existing job should succeed."""
        # Create a job first
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PL123456789",
            destination_service="spotify",
            destination_name="My Playlist",
            transfer_mode=TransferMode.CREATE,
        )
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)

        # Create source tracks
        tracks = [
            SourceTrack(
                position=0,
                title="Track 1",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="video_1",
                channel_title="Channel A",
            ),
            SourceTrack(
                position=1,
                title="Track 2",
                artist_names=["Artist B"],
                duration_seconds=240,
                video_id="video_2",
                channel_title="Channel B",
            ),
            SourceTrack(
                position=2,
                title="Track 3",
                artist_names=["Artist C"],
                duration_seconds=300,
                video_id="video_3",
                channel_title="Channel C",
            ),
        ]

        # Insert tracks
        count = bulk_insert_source_tracks(
            session=in_memory_session,
            job_id=job_id,
            tracks=tracks,
        )

        # Verify the count matches
        assert count == 3

        # Verify the tracks were actually inserted
        from playlist_bridge.persistence.models import SourceTrackRecord
        inserted = in_memory_session.query(SourceTrackRecord).filter_by(job_id=job_id).order_by(SourceTrackRecord.position).all()
        assert len(inserted) == 3
        assert inserted[0].source_item_id == "video_1"
        assert inserted[0].title == "Track 1"
        assert inserted[0].artist_names == ["Artist A"]
        assert inserted[0].duration_seconds == 180
        assert inserted[0].channel_title == "Channel A"
        assert inserted[1].source_item_id == "video_2"
        assert inserted[2].source_item_id == "video_3"

    def test_bulk_insert_job_not_found(self, in_memory_session: Session):
        """Bulk inserting tracks for a non-existent job should raise JobNotFoundError."""
        non_existent_job_id = str(uuid.uuid4())
        tracks = [
            SourceTrack(
                position=0,
                title="Track 1",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="video_1",
            ),
        ]

        with pytest.raises(JobNotFoundError) as exc_info:
            bulk_insert_source_tracks(
                session=in_memory_session,
                job_id=non_existent_job_id,
                tracks=tracks,
            )

        assert exc_info.value.job_id == non_existent_job_id
        assert str(exc_info.value) == f"Job not found: {non_existent_job_id}"

    def test_bulk_insert_empty_tracks(self, in_memory_session: Session):
        """Bulk inserting an empty list of tracks should return 0."""
        # Create a job first
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PL123456789",
            destination_service="spotify",
            destination_name="My Playlist",
            transfer_mode=TransferMode.CREATE,
        )
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)

        count = bulk_insert_source_tracks(
            session=in_memory_session,
            job_id=job_id,
            tracks=[],
        )

        assert count == 0

        # Verify no tracks were inserted
        from playlist_bridge.persistence.models import SourceTrackRecord
        inserted = in_memory_session.query(SourceTrackRecord).filter_by(job_id=job_id).all()
        assert len(inserted) == 0

    def test_bulk_insert_duplicate_item_raises_integrity_error(self, in_memory_session: Session):
        """Bulk inserting a duplicate source_item_id for the same job should raise IntegrityError."""
        # Create a job first
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="PL123456789",
            destination_service="spotify",
            destination_name="My Playlist",
            transfer_mode=TransferMode.CREATE,
        )
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)

        # Create tracks with duplicate video_id
        tracks = [
            SourceTrack(
                position=0,
                title="Track 1",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="duplicate_video",
            ),
            SourceTrack(
                position=1,
                title="Track 2",
                artist_names=["Artist B"],
                duration_seconds=240,
                video_id="duplicate_video",  # Duplicate ID
            ),
        ]

        # Inserting tracks with duplicate video_id should raise IntegrityError
        from playlist_bridge.ports import IntegrityError as DomainIntegrityError
        with pytest.raises(DomainIntegrityError):
            bulk_insert_source_tracks(
                session=in_memory_session,
                job_id=job_id,
                tracks=tracks,
            )
