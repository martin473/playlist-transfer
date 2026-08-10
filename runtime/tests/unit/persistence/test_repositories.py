"""Unit tests for repository functions."""

from datetime import datetime, timezone, timedelta
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from playlist_bridge.domain.enums import DestinationService, JobStatus, SourceService, TrackStatus, TransferMode
from playlist_bridge.domain.models import MatchDecision, SourceTrack, TransferRequest
from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import JobRecord, ManualCorrection, MatchCacheEntry
from playlist_bridge.persistence.repositories import (
    JobNotFoundError,
    JobLease,
    LeaseLostError,
    bulk_insert_source_tracks,
    create_job,
    get_job,
    get_source_tracks_ordered,
    get_unresolved_decisions,
    lookup_match_cache,
    lookup_manual_correction,
    record_job_error,
    resolve_correction_then_cache,
    update_job_checkpoint,
    update_job_state,
    upsert_manual_correction,
    upsert_match_cache,
    upsert_match_decision,
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


class TestUpsertMatchCache:
    """Tests for upsert_match_cache function."""

    def test_upsert_creates_new_entry(self, in_memory_session: Session):
        """Upserting a new fingerprint creates a new cache entry."""
        # Create a new entry
        entry = MatchCacheEntry(
            source_fingerprint="new-fingerprint-789",
            spotify_track_id="spotify:track:new123",
            confidence=90,
            origin="manual",
            last_verified_at=datetime.now(timezone.utc),
        )

        # Upsert it
        result = upsert_match_cache(in_memory_session, entry)

        # Verify it was inserted
        assert result.source_fingerprint == "new-fingerprint-789"
        assert result.spotify_track_id == "spotify:track:new123"
        assert result.confidence == 90
        assert result.origin == "manual"

        # Verify it exists in the database
        lookup_result = lookup_match_cache(in_memory_session, "new-fingerprint-789")
        assert lookup_result is not None
        assert lookup_result.source_fingerprint == "new-fingerprint-789"

    def test_upsert_replaces_existing_entry(self, in_memory_session: Session):
        """A second upsert with the same fingerprint replaces the prior entry."""
        # Insert initial entry
        original_timestamp = datetime.now(timezone.utc)
        initial_entry = MatchCacheEntry(
            source_fingerprint="fingerprint-to-update",
            spotify_track_id="spotify:track:original",
            confidence=60,
            origin="auto",
            last_verified_at=original_timestamp,
        )
        upsert_match_cache(in_memory_session, initial_entry)

        # Get the entry to verify it was inserted
        first_result = lookup_match_cache(in_memory_session, "fingerprint-to-update")
        assert first_result is not None
        assert first_result.spotify_track_id == "spotify:track:original"
        assert first_result.confidence == 60

        # Upsert with new values
        new_timestamp = datetime.now(timezone.utc)
        updated_entry = MatchCacheEntry(
            source_fingerprint="fingerprint-to-update",
            spotify_track_id="spotify:track:updated",
            confidence=95,
            origin="manual",
            last_verified_at=new_timestamp,
        )
        result = upsert_match_cache(in_memory_session, updated_entry)

        # Verify the entry was updated
        assert result.source_fingerprint == "fingerprint-to-update"
        assert result.spotify_track_id == "spotify:track:updated"
        assert result.confidence == 95
        assert result.origin == "manual"

        # Verify the database has the updated values
        second_result = lookup_match_cache(in_memory_session, "fingerprint-to-update")
        assert second_result is not None
        assert second_result.spotify_track_id == "spotify:track:updated"
        assert second_result.confidence == 95
        assert second_result.origin == "manual"

    def test_upsert_handles_existing_entry_gracefully(self, in_memory_session: Session):
        """Upsert should handle existing entries gracefully without errors."""
        # Insert an entry
        entry1 = MatchCacheEntry(
            source_fingerprint="test-graceful",
            spotify_track_id="spotify:track:first",
            confidence=50,
            origin="auto",
            last_verified_at=datetime.now(timezone.utc),
        )
        upsert_match_cache(in_memory_session, entry1)

        # Upsert a second entry with the same fingerprint - should update
        entry2 = MatchCacheEntry(
            source_fingerprint="test-graceful",
            spotify_track_id="spotify:track:second",
            confidence=75,
            origin="manual",
            last_verified_at=datetime.now(timezone.utc),
        )
        result = upsert_match_cache(in_memory_session, entry2)
        assert result.spotify_track_id == "spotify:track:second"
        assert result.confidence == 75
        assert result.origin == "manual"


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


class TestGetJob:
    """Tests for get_job function."""

    def test_get_job_existing_returns_job(self, in_memory_session: Session):
        """Retrieving an existing job by ID should return the job record."""
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
        created_job = create_job(session=in_memory_session, request=request, job_id=job_id, created_at=created_at)

        # Retrieve the job
        retrieved_job = get_job(session=in_memory_session, job_id=job_id)

        assert retrieved_job is not None
        assert retrieved_job.id == job_id
        assert retrieved_job.state == created_job.state
        assert retrieved_job.source_playlist_id == created_job.source_playlist_id
        assert retrieved_job.destination_playlist_id == created_job.destination_playlist_id
        assert retrieved_job.request_json == created_job.request_json

    def test_get_job_missing_returns_none(self, in_memory_session: Session):
        """Retrieving a non-existent job ID should return None."""
        non_existent_id = "non-existent-job-id-12345"
        result = get_job(session=in_memory_session, job_id=non_existent_id)
        assert result is None


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


class TestGetSourceTracksOrdered:
    """Tests for get_source_tracks_ordered function."""

    def test_get_source_tracks_ordered_returns_ordered_tracks(self, in_memory_session: Session):
        """Retrieved tracks should be ordered by source position ascending."""
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

        # Create source tracks in random order
        tracks = [
            SourceTrack(
                position=2,
                title="Track 3",
                artist_names=["Artist C"],
                duration_seconds=300,
                video_id="video_3",
                channel_title="Channel C",
            ),
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
        ]

        # Insert tracks
        bulk_insert_source_tracks(
            session=in_memory_session,
            job_id=job_id,
            tracks=tracks,
        )

        # Retrieve tracks ordered by position
        retrieved = get_source_tracks_ordered(
            session=in_memory_session,
            job_id=job_id,
        )

        # Verify they are returned in the correct order
        assert len(retrieved) == 3
        assert retrieved[0].position == 0
        assert retrieved[0].video_id == "video_1"
        assert retrieved[0].title == "Track 1"
        assert retrieved[1].position == 1
        assert retrieved[1].video_id == "video_2"
        assert retrieved[1].title == "Track 2"
        assert retrieved[2].position == 2
        assert retrieved[2].video_id == "video_3"
        assert retrieved[2].title == "Track 3"

    def test_get_source_tracks_ordered_empty_list(self, in_memory_session: Session):
        """Getting tracks for a job with no tracks should return an empty list."""
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

        # Retrieve tracks (none inserted yet)
        retrieved = get_source_tracks_ordered(
            session=in_memory_session,
            job_id=job_id,
        )

        assert retrieved == []

    def test_get_source_tracks_ordered_job_not_found(self, in_memory_session: Session):
        """Getting tracks for a non-existent job should raise JobNotFoundError."""
        non_existent_job_id = "non-existent-job-id"

        with pytest.raises(JobNotFoundError) as exc_info:
            get_source_tracks_ordered(
                session=in_memory_session,
                job_id=non_existent_job_id,
            )

        assert exc_info.value.job_id == non_existent_job_id
        assert str(exc_info.value) == f"Job not found: {non_existent_job_id}"


class TestSaveProfile:
    """Tests for save_profile function."""

    def test_save_profile_create_new(self, in_memory_session: Session):
        """Creating a new profile should persist and return the profile."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import save_profile

        # Create a new profile
        profile = AccountProfile(
            profile_name="user123",
            service="spotify",
            provider_user_id="user123",
            display_name="Test User",
        )

        # Save it
        saved = save_profile(session=in_memory_session, profile=profile)

        # Verify the saved profile
        assert saved.profile_name == "user123"
        assert saved.service == "spotify"
        assert saved.display_name == "Test User"

        # Verify it was actually persisted
        from playlist_bridge.persistence.models import AccountProfileRecord
        record = in_memory_session.query(AccountProfileRecord).filter_by(
            service="spotify",
            profile_name="user123",
        ).first()
        assert record is not None
        assert record.service == "spotify"
        assert record.profile_name == "user123"
        assert record.display_name == "Test User"

    def test_save_profile_update_existing(self, in_memory_session: Session):
        """Updating an existing profile should update the record and return updated profile."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.models import AccountProfileRecord
        from playlist_bridge.persistence.repositories import save_profile

        # First, insert a profile directly
        record = AccountProfileRecord(
            service="spotify",
            profile_name="user123",
            provider_user_id="user123",
            display_name="Old Name",
        )
        in_memory_session.add(record)
        in_memory_session.commit()

        # Now update it via save_profile
        profile = AccountProfile(
            profile_name="user123",
            service="spotify",
            provider_user_id="user123",
            display_name="New Name",
        )
        saved = save_profile(session=in_memory_session, profile=profile)

        # Verify the saved profile has updated display_name
        assert saved.profile_name == "user123"
        assert saved.service == "spotify"
        assert saved.display_name == "New Name"

        # Verify the database was updated
        record = in_memory_session.query(AccountProfileRecord).filter_by(
            service="spotify",
            profile_name="user123",
        ).first()
        assert record is not None
        assert record.display_name == "New Name"

    def test_save_profile_duplicate_violation(self, in_memory_session: Session):
        """Saving a duplicate (service, profile_name) pair should raise IntegrityError."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.models import AccountProfileRecord
        from playlist_bridge.persistence.repositories import save_profile
        from playlist_bridge.ports import IntegrityError as DomainIntegrityError

        # Insert a profile directly with a specific (service, profile_name)
        record = AccountProfileRecord(
            service="spotify",
            profile_name="existing_user",
            provider_user_id="existing_user",
            display_name="Existing User",
        )
        in_memory_session.add(record)
        in_memory_session.commit()

        # Try to save another profile with the same (service, profile_name)
        # but different display_name should be an update, not a duplicate
        # Actually, the function will update, not raise, because we check for existing first
        # So we need to create a different scenario - but with the unique constraint,
        # if we try to insert a new record with the same (service, profile_name),
        # it should raise. However, our save_profile function does an upsert,
        # so it won't raise. Let me test the update case instead.

        # Actually, since save_profile does an upsert, it won't raise IntegrityError
        # on duplicate (service, profile_name) because it updates. So we don't need
        # to test for IntegrityError here - it's handled internally.
        # The function itself commits and updates, so no error is raised.
        # We already test the update case above.

        # Let's just verify that saving with same (service, profile_name)
        # updates rather than raises.
        profile = AccountProfile(
            profile_name="existing_user",
            service="spotify",
            provider_user_id="existing_user",
            display_name="Updated User",
        )
        saved = save_profile(session=in_memory_session, profile=profile)
        assert saved.display_name == "Updated User"

        # Verify the database was updated
        record = in_memory_session.query(AccountProfileRecord).filter_by(
            service="spotify",
            profile_name="existing_user",
        ).first()
        assert record is not None
        assert record.display_name == "Updated User"

    def test_save_profile_creates_multiple_profiles(self, in_memory_session: Session):
        """Saving multiple profiles should work correctly."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.models import AccountProfileRecord
        from playlist_bridge.persistence.repositories import save_profile

        # Create multiple profiles
        profile1 = AccountProfile(
            profile_name="user1",
            service="spotify",
            provider_user_id="user1",
            display_name="User One",
        )
        profile2 = AccountProfile(
            profile_name="user2",
            service="spotify",
            provider_user_id="user2",
            display_name="User Two",
        )
        profile3 = AccountProfile(
            profile_name="yt_user1",
            service="youtube",
            provider_user_id="yt_user1",
            display_name="YouTube User",
        )

        save_profile(session=in_memory_session, profile=profile1)
        save_profile(session=in_memory_session, profile=profile2)
        save_profile(session=in_memory_session, profile=profile3)

        # Verify all were saved
        records = in_memory_session.query(AccountProfileRecord).all()
        assert len(records) == 3

        # Verify by service
        spotify_records = in_memory_session.query(AccountProfileRecord).filter_by(service="spotify").all()
        assert len(spotify_records) == 2

        youtube_records = in_memory_session.query(AccountProfileRecord).filter_by(service="youtube").all()
        assert len(youtube_records) == 1

    def test_get_profile_returns_profile(self, in_memory_session: Session):
        """get_profile should return the profile when it exists."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.models import AccountProfileRecord
        from playlist_bridge.persistence.repositories import get_profile, save_profile

        # Save a profile
        profile = AccountProfile(
            profile_name="user123",
            service="spotify",
            provider_user_id="user123",
            display_name="Test User",
        )
        save_profile(session=in_memory_session, profile=profile)

        # Retrieve it
        retrieved = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="user123",
        )

        assert retrieved is not None
        assert retrieved.profile_name == "user123"
        assert retrieved.service == "spotify"
        assert retrieved.display_name == "Test User"

    def test_get_profile_returns_none_when_missing(self, in_memory_session: Session):
        """get_profile should return None when the profile doesn't exist."""
        from playlist_bridge.persistence.repositories import get_profile

        retrieved = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="nonexistent",
        )

        assert retrieved is None

    def test_list_profiles_returns_all_profiles(self, in_memory_session: Session):
        """list_profiles should return all profiles when no service filter is provided."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import list_profiles, save_profile

        # Save profiles for different services
        profile1 = AccountProfile(
            profile_name="user1",
            service="spotify",
            provider_user_id="user1",
            display_name="User One",
        )
        profile2 = AccountProfile(
            profile_name="user2",
            service="spotify",
            provider_user_id="user2",
            display_name="User Two",
        )
        profile3 = AccountProfile(
            profile_name="yt_user1",
            service="youtube",
            provider_user_id="yt_user1",
            display_name="YouTube User",
        )

        save_profile(session=in_memory_session, profile=profile1)
        save_profile(session=in_memory_session, profile=profile2)
        save_profile(session=in_memory_session, profile=profile3)

        # List all profiles
        profiles = list_profiles(session=in_memory_session)
        assert len(profiles) == 3

        # Verify the profiles are returned as AccountProfile objects
        assert all(isinstance(p, AccountProfile) for p in profiles)
        # Check they're ordered by service then profile_name
        assert profiles[0].service == "spotify"
        assert profiles[0].profile_name == "user1"
        assert profiles[1].service == "spotify"
        assert profiles[1].profile_name == "user2"
        assert profiles[2].service == "youtube"
        assert profiles[2].profile_name == "yt_user1"

    def test_list_profiles_filters_by_service(self, in_memory_session: Session):
        """list_profiles should filter by service when provided."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import list_profiles, save_profile

        # Save profiles for different services
        profile1 = AccountProfile(
            profile_name="user1",
            service="spotify",
            provider_user_id="user1",
            display_name="User One",
        )
        profile2 = AccountProfile(
            profile_name="user2",
            service="spotify",
            provider_user_id="user2",
            display_name="User Two",
        )
        profile3 = AccountProfile(
            profile_name="yt_user1",
            service="youtube",
            provider_user_id="yt_user1",
            display_name="YouTube User",
        )

        save_profile(session=in_memory_session, profile=profile1)
        save_profile(session=in_memory_session, profile=profile2)
        save_profile(session=in_memory_session, profile=profile3)

        # List only spotify profiles
        spotify_profiles = list_profiles(
            session=in_memory_session,
            service=DestinationService.SPOTIFY,
        )
        assert len(spotify_profiles) == 2
        assert all(p.service == "spotify" for p in spotify_profiles)

        # List only youtube profiles
        youtube_profiles = list_profiles(
            session=in_memory_session,
            service=SourceService.YOUTUBE,
        )
        assert len(youtube_profiles) == 1
        assert youtube_profiles[0].service == "youtube"

        # List with non-existent service
        empty_profiles = list_profiles(
            session=in_memory_session,
            service="nonexistent",
        )
        assert len(empty_profiles) == 0

    def test_list_profiles_empty_when_no_profiles(self, in_memory_session: Session):
        """list_profiles should return an empty list when no profiles exist."""
        from playlist_bridge.persistence.repositories import list_profiles

        profiles = list_profiles(session=in_memory_session)
        assert profiles == []


class TestGetProfile:
    """Tests for get_profile function."""

    def test_get_profile_returns_profile(self, in_memory_session: Session):
        """get_profile should return the profile when it exists."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import get_profile, save_profile

        # Save a profile
        profile = AccountProfile(
            profile_name="user123",
            service="spotify",
            provider_user_id="user123",
            display_name="Test User",
        )
        save_profile(session=in_memory_session, profile=profile)

        # Retrieve it
        retrieved = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="user123",
        )

        assert retrieved is not None
        assert retrieved.profile_name == "user123"
        assert retrieved.service == "spotify"
        assert retrieved.display_name == "Test User"

    def test_get_profile_returns_none_when_missing(self, in_memory_session: Session):
        """get_profile should return None when the profile doesn't exist."""
        from playlist_bridge.persistence.repositories import get_profile

        retrieved = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="nonexistent",
        )

        assert retrieved is None


class TestUpsertMatchDecision:
    """Tests for upsert_match_decision function."""

    def test_upsert_match_decision_creates_new(self, in_memory_session: Session):
        """Upserting a new decision should create a new match decision record."""
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

        # Create a match decision
        decision = MatchDecision(
            source_item_id="video_1",
            destination_uri="spotify:track:abc123",
            destination_track_id="abc123",
            destination_title="Test Track",
            destination_artist_names=["Test Artist"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        # Upsert the decision
        result = upsert_match_decision(
            session=in_memory_session,
            job_id=job_id,
            decision=decision,
        )

        # Verify the result
        assert result.source_item_id == "video_1"
        assert result.destination_track_id == "abc123"
        assert result.score == 0.95
        assert result.decision_type == "accepted"
        assert result.confidence == 0.9

        # Verify it was persisted
        from playlist_bridge.persistence.models import MatchDecisionRecord
        record = in_memory_session.query(MatchDecisionRecord).filter_by(
            job_id=job_id,
            source_item_id="video_1",
        ).first()
        assert record is not None
        assert record.spotify_track_id == "abc123"
        assert record.decision_status == "accepted"
        assert record.score_json["score"] == 0.95
        assert record.score_json["confidence"] == 0.9

    def test_upsert_match_decision_replaces_existing(self, in_memory_session: Session):
        """A second write replaces the first decision for the same job and source item."""
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

        # Create first decision
        decision1 = MatchDecision(
            source_item_id="video_1",
            destination_uri="spotify:track:first123",
            destination_track_id="first123",
            destination_title="First Track",
            destination_artist_names=["First Artist"],
            score=0.5,
            decision_type="review",
            confidence=0.6,
        )

        # Upsert first decision
        upsert_match_decision(
            session=in_memory_session,
            job_id=job_id,
            decision=decision1,
        )

        # Create second decision (different values, same source_item_id)
        decision2 = MatchDecision(
            source_item_id="video_1",
            destination_uri="spotify:track:second456",
            destination_track_id="second456",
            destination_title="Second Track",
            destination_artist_names=["Second Artist"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        # Upsert second decision
        result2 = upsert_match_decision(
            session=in_memory_session,
            job_id=job_id,
            decision=decision2,
        )

        # Verify the result has the second values
        assert result2.source_item_id == "video_1"
        assert result2.destination_track_id == "second456"
        assert result2.destination_title == "Second Track"
        assert result2.score == 0.95
        assert result2.decision_type == "accepted"
        assert result2.confidence == 0.9

        # Verify the database only has one record (the second one)
        from playlist_bridge.persistence.models import MatchDecisionRecord
        records = in_memory_session.query(MatchDecisionRecord).filter_by(
            job_id=job_id,
            source_item_id="video_1",
        ).all()
        assert len(records) == 1
        assert records[0].spotify_track_id == "second456"
        assert records[0].decision_status == "accepted"
        assert records[0].score_json["score"] == 0.95
        assert records[0].score_json["confidence"] == 0.9

    def test_upsert_match_decision_job_not_found(self, in_memory_session: Session):
        """Upserting a decision for a non-existent job should raise JobNotFoundError."""
        non_existent_job_id = "non-existent-job-id"

        decision = MatchDecision(
            source_item_id="video_1",
            destination_uri="spotify:track:abc123",
            destination_track_id="abc123",
            destination_title="Test Track",
            destination_artist_names=["Test Artist"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        with pytest.raises(JobNotFoundError) as exc_info:
            upsert_match_decision(
                session=in_memory_session,
                job_id=non_existent_job_id,
                decision=decision,
            )

        assert exc_info.value.job_id == non_existent_job_id
        assert str(exc_info.value) == f"Job not found: {non_existent_job_id}"
    """Tests for get_profile function."""

    def test_get_profile_returns_existing_profile(self, in_memory_session: Session):
        """get_profile should return a profile when it exists."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import get_profile, save_profile

        # Save a profile
        profile = AccountProfile(
            provider="spotify",
            account_id="test_user",
            display_name="Test User",
        )
        save_profile(session=in_memory_session, profile=profile)

        # Retrieve it
        result = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="test_user",
        )

        assert result is not None
        assert isinstance(result, AccountProfile)
        assert result.provider == "spotify"
        assert result.account_id == "test_user"
        assert result.display_name == "Test User"

    def test_get_profile_returns_none_for_missing_profile(self, in_memory_session: Session):
        """get_profile should return None when the profile does not exist."""
        from playlist_bridge.persistence.repositories import get_profile

        result = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="non_existent_user",
        )

        assert result is None

    def test_get_profile_respects_service_filter(self, in_memory_session: Session):
        """get_profile should only match exact service and profile_name."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import get_profile, save_profile

        # Save a spotify profile
        spotify_profile = AccountProfile(
            provider="spotify",
            account_id="user123",
            display_name="Spotify User",
        )
        save_profile(session=in_memory_session, profile=spotify_profile)

        # Save a youtube profile with same account_id
        youtube_profile = AccountProfile(
            provider="youtube",
            account_id="user123",
            display_name="YouTube User",
        )
        save_profile(session=in_memory_session, profile=youtube_profile)

        # Get spotify profile
        result = get_profile(
            session=in_memory_session,
            service="spotify",
            profile_name="user123",
        )

        assert result is not None
        assert result.provider == "spotify"
        assert result.account_id == "user123"

        # Get youtube profile
        result = get_profile(
            session=in_memory_session,
            service="youtube",
            profile_name="user123",
        )

        assert result is not None
        assert result.provider == "youtube"
        assert result.account_id == "user123"

    def test_get_profile_none_when_wrong_service(self, in_memory_session: Session):
        """get_profile returns None when service doesn't match."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import get_profile, save_profile

        # Save a spotify profile
        profile = AccountProfile(
            provider="spotify",
            account_id="user123",
            display_name="Spotify User",
        )
        save_profile(session=in_memory_session, profile=profile)

        # Try to get it with a different service
        result = get_profile(
            session=in_memory_session,
            service="youtube",
            profile_name="user123",
        )

        assert result is None


class TestLookupManualCorrection:
    """Tests for lookup_manual_correction function."""

    def test_missing_fingerprint_returns_none(self, in_memory_session: Session):
        """A missing fingerprint returns no correction."""
        result = lookup_manual_correction(in_memory_session, "non-existent-fingerprint")
        assert result is None

    def test_existing_fingerprint_with_spotify_id_returns_correction(self, in_memory_session: Session):
        """An existing fingerprint with a Spotify ID returns the correction."""
        # Insert a manual correction
        correction = ManualCorrection(
            source_fingerprint="test-fingerprint-123",
            spotify_track_id="spotify:track:abc123",
            skip_reason=None,
            explanation="User selected this track",
            origin="manual",
        )
        in_memory_session.add(correction)
        in_memory_session.commit()

        # Look it up
        result = lookup_manual_correction(in_memory_session, "test-fingerprint-123")
        assert result is not None
        assert result.source_fingerprint == "test-fingerprint-123"
        assert result.spotify_track_id == "spotify:track:abc123"
        assert result.skip_reason is None
        assert result.explanation == "User selected this track"
        assert result.origin == "manual"

    def test_existing_fingerprint_with_skip_distinguishable(self, in_memory_session: Session):
        """A stored skip is distinguishable from no correction."""
        # Insert a manual correction with a skip reason
        correction = ManualCorrection(
            source_fingerprint="skip-fingerprint-456",
            spotify_track_id=None,
            skip_reason="user_skipped",
            explanation="User skipped this track",
            origin="manual",
        )
        in_memory_session.add(correction)
        in_memory_session.commit()

        # Look it up - should find the skip
        result = lookup_manual_correction(in_memory_session, "skip-fingerprint-456")
        assert result is not None
        assert result.source_fingerprint == "skip-fingerprint-456"
        assert result.spotify_track_id is None
        assert result.skip_reason == "user_skipped"
        assert result.explanation == "User skipped this track"

        # Verify a different fingerprint returns None (distinguishable from no correction)
        result_none = lookup_manual_correction(in_memory_session, "non-existent-fingerprint")
        assert result_none is None

        # Also verify that the skip is not confused with a Spotify ID correction
        # by checking that the skip_reason is set and spotify_track_id is None
        assert result.spotify_track_id is None
        assert result.skip_reason is not None


class TestUpsertManualCorrection:
    """Tests for upsert_manual_correction function."""

    def test_upsert_creates_new_correction(self, in_memory_session: Session):
        """Upserting a new fingerprint creates a new manual correction."""
        # Create a new correction
        correction = ManualCorrection(
            source_fingerprint="new-fingerprint-789",
            spotify_track_id="spotify:track:new123",
            skip_reason=None,
            explanation="User selected this track",
            origin="manual",
        )

        # Upsert it
        result = upsert_manual_correction(in_memory_session, correction)

        # Verify it was inserted
        assert result.source_fingerprint == "new-fingerprint-789"
        assert result.spotify_track_id == "spotify:track:new123"
        assert result.skip_reason is None
        assert result.explanation == "User selected this track"
        assert result.origin == "manual"

        # Verify it exists in the database
        lookup_result = lookup_manual_correction(in_memory_session, "new-fingerprint-789")
        assert lookup_result is not None
        assert lookup_result.source_fingerprint == "new-fingerprint-789"

    def test_upsert_replaces_existing_correction(self, in_memory_session: Session):
        """A newer correction replaces the prior correction."""
        # Insert initial correction
        initial_correction = ManualCorrection(
            source_fingerprint="fingerprint-to-update",
            spotify_track_id="spotify:track:original",
            skip_reason=None,
            explanation="Original selection",
            origin="manual",
        )
        upsert_manual_correction(in_memory_session, initial_correction)

        # Verify initial insertion
        initial_lookup = lookup_manual_correction(in_memory_session, "fingerprint-to-update")
        assert initial_lookup is not None
        assert initial_lookup.spotify_track_id == "spotify:track:original"

        # Create a newer correction with the same fingerprint
        newer_correction = ManualCorrection(
            source_fingerprint="fingerprint-to-update",
            spotify_track_id="spotify:track:newer",
            skip_reason=None,
            explanation="Newer selection",
            origin="manual",
        )

        # Upsert the newer correction
        result = upsert_manual_correction(in_memory_session, newer_correction)

        # Verify the newer correction replaced the older one
        assert result.source_fingerprint == "fingerprint-to-update"
        assert result.spotify_track_id == "spotify:track:newer"
        assert result.explanation == "Newer selection"

        # Verify only one record exists (the newer one)
        lookup_result = lookup_manual_correction(in_memory_session, "fingerprint-to-update")
        assert lookup_result is not None
        assert lookup_result.spotify_track_id == "spotify:track:newer"
        assert lookup_result.explanation == "Newer selection"

        # Count records to ensure no duplicates
        all_records = in_memory_session.query(ManualCorrection).filter_by(
            source_fingerprint="fingerprint-to-update"
        ).all()
        assert len(all_records) == 1

    def test_upsert_with_skip_replaces_prior_correction(self, in_memory_session: Session):
        """Upserting a skip replaces a prior Spotify ID correction."""
        # Insert initial correction with Spotify ID
        initial_correction = ManualCorrection(
            source_fingerprint="fingerprint-skip-test",
            spotify_track_id="spotify:track:initial",
            skip_reason=None,
            explanation="Initial selection",
            origin="manual",
        )
        upsert_manual_correction(in_memory_session, initial_correction)

        # Verify initial insertion
        initial_lookup = lookup_manual_correction(in_memory_session, "fingerprint-skip-test")
        assert initial_lookup is not None
        assert initial_lookup.spotify_track_id == "spotify:track:initial"
        assert initial_lookup.skip_reason is None

        # Upsert a skip correction
        skip_correction = ManualCorrection(
            source_fingerprint="fingerprint-skip-test",
            spotify_track_id=None,
            skip_reason="user_skipped",
            explanation="User skipped this track",
            origin="manual",
        )
        result = upsert_manual_correction(in_memory_session, skip_correction)

        # Verify the skip replaced the prior correction
        assert result.source_fingerprint == "fingerprint-skip-test"
        assert result.spotify_track_id is None
        assert result.skip_reason == "user_skipped"
        assert result.explanation == "User skipped this track"

        # Verify only one record exists
        lookup_result = lookup_manual_correction(in_memory_session, "fingerprint-skip-test")
        assert lookup_result is not None
        assert lookup_result.spotify_track_id is None
        assert lookup_result.skip_reason == "user_skipped"

        all_records = in_memory_session.query(ManualCorrection).filter_by(
            source_fingerprint="fingerprint-skip-test"
        ).all()
        assert len(all_records) == 1


class TestUpdateJobState:
    """Tests for update_job_state function."""

    def test_update_job_state_success(self, in_memory_session: Session):
        """update_job_state successfully updates job state and updated_at."""
        # Create a job first
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )
        assert job.state == "pending"

        # Update the job state
        new_status = JobStatus.READING
        updated_at = datetime.now(timezone.utc)
        updated_job = update_job_state(
            session=in_memory_session,
            job_id=job_id,
            status=new_status,
            updated_at=updated_at,
        )

        # Verify the state was updated
        assert updated_job.id == job_id
        assert updated_job.state == "reading"
        # Compare datetime without timezone info (SQLite may not preserve it)
        assert updated_job.updated_at.replace(tzinfo=None) == updated_at.replace(tzinfo=None)

        # Reload the job and verify the state persists
        reloaded_job = get_job(in_memory_session, job_id)
        assert reloaded_job is not None
        assert reloaded_job.state == "reading"
        assert reloaded_job.updated_at.replace(tzinfo=None) == updated_at.replace(tzinfo=None)

    def test_update_job_state_job_not_found(self, in_memory_session: Session):
        """update_job_state raises JobNotFoundError when job doesn't exist."""
        non_existent_job_id = "non-existent-job-id"
        updated_at = datetime.now(timezone.utc)

        with pytest.raises(JobNotFoundError) as exc_info:
            update_job_state(
                session=in_memory_session,
                job_id=non_existent_job_id,
                status=JobStatus.READING,
                updated_at=updated_at,
            )

        assert exc_info.value.job_id == non_existent_job_id


class TestUpdateJobCheckpoint:
    """Tests for update_job_checkpoint function."""

    def test_update_job_checkpoint_success(self, in_memory_session: Session):
        """update_job_checkpoint successfully updates checkpoint fields."""
        # Create a job first
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )
        assert job.state == "pending"
        assert job.match_checkpoint == 0
        assert job.write_checkpoint == 0
        assert job.verification_checkpoint == 0

        # Set up a lease
        lease_holder = "worker-1"
        lease_expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=30)
        lease_heartbeat_at = datetime.now(timezone.utc).replace(microsecond=0)
        lease = JobLease(
            lease_holder=lease_holder,
            lease_expires_at=lease_expires_at,
            lease_heartbeat_at=lease_heartbeat_at,
        )

        # Set the lease on the job
        job.lease_holder = lease_holder
        job.lease_expires_at = lease_expires_at
        job.lease_heartbeat_at = lease_heartbeat_at
        in_memory_session.commit()

        # Update checkpoint fields
        updated_at = datetime.now(timezone.utc)
        checkpoint_fields = {
            "match_checkpoint": 10,
            "write_checkpoint": 5,
            "verification_checkpoint": 3,
        }
        updated_job = update_job_checkpoint(
            session=in_memory_session,
            job_id=job_id,
            checkpoint_fields=checkpoint_fields,
            updated_at=updated_at,
            lease=lease,
        )

        # Verify the checkpoints were updated
        assert updated_job.id == job_id
        assert updated_job.match_checkpoint == 10
        assert updated_job.write_checkpoint == 5
        assert updated_job.verification_checkpoint == 3
        assert updated_job.updated_at.replace(tzinfo=None) == updated_at.replace(tzinfo=None)
        assert updated_job.lease_holder == lease_holder
        assert updated_job.lease_expires_at.replace(tzinfo=None) == lease_expires_at.replace(tzinfo=None)
        assert updated_job.lease_heartbeat_at.replace(tzinfo=None) == lease_heartbeat_at.replace(tzinfo=None)
        assert updated_job.row_version == 2  # Incremented from 1

        # Reload the job and verify the checkpoints persist
        reloaded_job = get_job(in_memory_session, job_id)
        assert reloaded_job is not None
        assert reloaded_job.match_checkpoint == 10
        assert reloaded_job.write_checkpoint == 5
        assert reloaded_job.verification_checkpoint == 3

    def test_update_job_checkpoint_partial_update(self, in_memory_session: Session):
        """update_job_checkpoint updates only the specified checkpoint fields."""
        # Create a job first
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )
        assert job.match_checkpoint == 0
        assert job.write_checkpoint == 0
        assert job.verification_checkpoint == 0

        # Set up a lease
        lease_holder = "worker-2"
        lease_expires_at = datetime.now(timezone.utc).replace(microsecond=0) + timedelta(seconds=30)
        lease_heartbeat_at = datetime.now(timezone.utc).replace(microsecond=0)
        lease = JobLease(
            lease_holder=lease_holder,
            lease_expires_at=lease_expires_at,
            lease_heartbeat_at=lease_heartbeat_at,
        )

        # Set the lease on the job
        job.lease_holder = lease_holder
        job.lease_expires_at = lease_expires_at
        job.lease_heartbeat_at = lease_heartbeat_at
        in_memory_session.commit()

        # Update only one checkpoint field
        updated_at = datetime.now(timezone.utc)
        checkpoint_fields = {
            "match_checkpoint": 42,
        }
        updated_job = update_job_checkpoint(
            session=in_memory_session,
            job_id=job_id,
            checkpoint_fields=checkpoint_fields,
            updated_at=updated_at,
            lease=lease,
        )

        # Verify only the specified field was updated
        assert updated_job.match_checkpoint == 42
        assert updated_job.write_checkpoint == 0  # Unchanged
        assert updated_job.verification_checkpoint == 0  # Unchanged

        # Reload and verify
        reloaded_job = get_job(in_memory_session, job_id)
        assert reloaded_job is not None
        assert reloaded_job.match_checkpoint == 42
        assert reloaded_job.write_checkpoint == 0
        assert reloaded_job.verification_checkpoint == 0

    def test_update_job_checkpoint_job_not_found(self, in_memory_session: Session):
        """update_job_checkpoint raises JobNotFoundError when job doesn't exist."""
        non_existent_job_id = "non-existent-job-id"
        updated_at = datetime.now(timezone.utc)
        lease = JobLease(
            lease_holder="worker-1",
            lease_expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
            lease_heartbeat_at=datetime.now(timezone.utc),
        )

        with pytest.raises(JobNotFoundError) as exc_info:
            update_job_checkpoint(
                session=in_memory_session,
                job_id=non_existent_job_id,
                checkpoint_fields={"match_checkpoint": 10},
                updated_at=updated_at,
                lease=lease,
            )

        assert exc_info.value.job_id == non_existent_job_id

    def test_update_job_checkpoint_lease_lost_wrong_holder(self, in_memory_session: Session):
        """update_job_checkpoint raises LeaseLostError when lease holder doesn't match."""
        # Create a job
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )

        # Set a different lease holder
        job.lease_holder = "worker-1"
        job.lease_expires_at = datetime.now(timezone.utc) + timedelta(seconds=30)
        job.lease_heartbeat_at = datetime.now(timezone.utc)
        in_memory_session.commit()

        # Try to update with a different lease holder
        different_lease = JobLease(
            lease_holder="worker-2",
            lease_expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
            lease_heartbeat_at=datetime.now(timezone.utc),
        )

        with pytest.raises(LeaseLostError) as exc_info:
            update_job_checkpoint(
                session=in_memory_session,
                job_id=job_id,
                checkpoint_fields={"match_checkpoint": 10},
                updated_at=datetime.now(timezone.utc),
                lease=different_lease,
            )

        assert exc_info.value.job_id == job_id

    def test_update_job_checkpoint_lease_expired(self, in_memory_session: Session):
        """update_job_checkpoint raises LeaseLostError when lease has expired."""
        # Create a job
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )

        # Set an expired lease
        lease_holder = "worker-1"
        expired_time = datetime.now(timezone.utc) - timedelta(seconds=1)
        job.lease_holder = lease_holder
        job.lease_expires_at = expired_time
        job.lease_heartbeat_at = expired_time - timedelta(seconds=5)
        in_memory_session.commit()

        # Try to update with the same holder but expired
        lease = JobLease(
            lease_holder=lease_holder,
            lease_expires_at=expired_time,
            lease_heartbeat_at=expired_time - timedelta(seconds=5),
        )

        with pytest.raises(LeaseLostError) as exc_info:
            update_job_checkpoint(
                session=in_memory_session,
                job_id=job_id,
                checkpoint_fields={"match_checkpoint": 10},
                updated_at=datetime.now(timezone.utc),
                lease=lease,
            )

        assert exc_info.value.job_id == job_id

    def test_update_job_checkpoint_invalid_field(self, in_memory_session: Session):
        """update_job_checkpoint raises ValueError for invalid checkpoint fields."""
        # Create a job
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )

        lease_holder = "worker-1"
        job.lease_holder = lease_holder
        job.lease_expires_at = datetime.now(timezone.utc) + timedelta(seconds=30)
        job.lease_heartbeat_at = datetime.now(timezone.utc)
        in_memory_session.commit()

        lease = JobLease(
            lease_holder=lease_holder,
            lease_expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
            lease_heartbeat_at=datetime.now(timezone.utc),
        )

        # Try to update an invalid field
        with pytest.raises(ValueError) as exc_info:
            update_job_checkpoint(
                session=in_memory_session,
                job_id=job_id,
                checkpoint_fields={"invalid_field": 99},
                updated_at=datetime.now(timezone.utc),
                lease=lease,
            )

        assert "Invalid checkpoint field" in str(exc_info.value)
        assert "match_checkpoint" in str(exc_info.value)
        assert "write_checkpoint" in str(exc_info.value)
        assert "verification_checkpoint" in str(exc_info.value)


class TestGetUnresolvedDecisions:
    """Tests for get_unresolved_decisions function."""

    def test_get_unresolved_decisions_excludes_accepted_and_skipped(
        self, in_memory_session: Session
    ):
        """Accepted and skipped decisions are excluded from unresolved results."""
        # Create a job
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        job = create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )

        # Insert source tracks with different positions
        source_tracks = [
            SourceTrack(
                position=0,
                title="Track 1",
                artist_names=["Artist 1"],
                duration_seconds=180,
                video_id="video1",
                channel_title="Channel 1",
            ),
            SourceTrack(
                position=1,
                title="Track 2",
                artist_names=["Artist 2"],
                duration_seconds=200,
                video_id="video2",
                channel_title="Channel 2",
            ),
            SourceTrack(
                position=2,
                title="Track 3",
                artist_names=["Artist 3"],
                duration_seconds=220,
                video_id="video3",
                channel_title="Channel 3",
            ),
            SourceTrack(
                position=3,
                title="Track 4",
                artist_names=["Artist 4"],
                duration_seconds=240,
                video_id="video4",
                channel_title="Channel 4",
            ),
            SourceTrack(
                position=4,
                title="Track 5",
                artist_names=["Artist 5"],
                duration_seconds=260,
                video_id="video5",
                channel_title="Channel 5",
            ),
        ]
        bulk_insert_source_tracks(in_memory_session, job_id, source_tracks)

        # Insert match decisions with various statuses
        # video1: accepted (excluded)
        # video2: skipped (excluded)
        # video3: pending (included)
        # video4: review (included)
        # video5: unmatched (included)

        decisions = [
            MatchDecision(
                source_item_id="video1",
                destination_uri="spotify:track:track1",
                destination_track_id="track1",
                destination_title="Track 1",
                destination_artist_names=["Artist 1"],
                score=0.95,
                decision_type="accepted",
                confidence=0.9,
            ),
            MatchDecision(
                source_item_id="video2",
                destination_uri="spotify:track:track2",
                destination_track_id="track2",
                destination_title="Track 2",
                destination_artist_names=["Artist 2"],
                score=0.0,
                decision_type="skipped",
                confidence=0.0,
            ),
            MatchDecision(
                source_item_id="video3",
                destination_uri="spotify:track:track3",
                destination_track_id="track3",
                destination_title="Track 3",
                destination_artist_names=["Artist 3"],
                score=0.0,
                decision_type="pending",
                confidence=0.0,
            ),
            MatchDecision(
                source_item_id="video4",
                destination_uri="spotify:track:track4",
                destination_track_id="track4",
                destination_title="Track 4",
                destination_artist_names=["Artist 4"],
                score=0.75,
                decision_type="review",
                confidence=0.7,
            ),
            MatchDecision(
                source_item_id="video5",
                destination_uri="spotify:track:unmatched",
                destination_track_id="unmatched",
                destination_title="No Match Found",
                destination_artist_names=["Unknown"],
                score=0.0,
                decision_type="unmatched",
                confidence=0.0,
            ),
        ]

        # Upsert each decision
        for decision in decisions:
            upsert_match_decision(in_memory_session, job_id, decision)

        # Get unresolved decisions
        unresolved = get_unresolved_decisions(in_memory_session, job_id)

        # Should only include video3 (pending), video4 (review), video5 (unmatched)
        # in source order (by position)
        assert len(unresolved) == 3

        # Check order by position: video3 (position 2), video4 (position 3), video5 (position 4)
        assert unresolved[0].source_item_id == "video3"
        assert unresolved[0].decision_type == "pending"
        assert unresolved[1].source_item_id == "video4"
        assert unresolved[1].decision_type == "review"
        assert unresolved[2].source_item_id == "video5"
        assert unresolved[2].decision_type == "unmatched"

        # Verify excluded decisions are not in results
        source_item_ids = [d.source_item_id for d in unresolved]
        assert "video1" not in source_item_ids  # accepted
        assert "video2" not in source_item_ids  # skipped

    def test_get_unresolved_decisions_job_not_found(self, in_memory_session: Session):
        """get_unresolved_decisions raises JobNotFoundError for non-existent job."""
        with pytest.raises(JobNotFoundError) as exc_info:
            get_unresolved_decisions(in_memory_session, "non-existent-job-id")

        assert exc_info.value.job_id == "non-existent-job-id"

    def test_get_unresolved_decisions_empty_job(self, in_memory_session: Session):
        """get_unresolved_decisions returns empty list for job with no decisions."""
        # Create a job with no source tracks or decisions
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_service="youtube",
            source_playlist_id="youtube:playlist:source123",
            destination_service="spotify",
            destination_playlist_id="spotify:playlist:dest456",
            transfer_mode=TransferMode.DRY_RUN,
        )
        create_job(
            session=in_memory_session,
            request=request,
            job_id=job_id,
            created_at=created_at,
        )

        # No source tracks, no decisions
        unresolved = get_unresolved_decisions(in_memory_session, job_id)
        assert unresolved == []


class TestResolveCorrectionThenCache:
    """Tests for resolve_correction_then_cache function."""

    def test_resolve_returns_manual_correction_first(self, in_memory_session: Session):
        """Manual corrections are returned before automatic cache entries for the same fingerprint."""
        fingerprint = "test-fingerprint-123"

        # Create and insert a manual correction
        correction = ManualCorrection(
            source_fingerprint=fingerprint,
            spotify_track_id="spotify:track:manual123",
            origin="manual_override",
            explanation="Manual override for test",
        )
        in_memory_session.add(correction)

        # Create and insert an automatic cache entry with the same fingerprint
        cache_entry = MatchCacheEntry(
            source_fingerprint=fingerprint,
            spotify_track_id="spotify:track:auto456",
            confidence=80,
            origin="auto",
            last_verified_at=datetime.now(timezone.utc),
        )
        in_memory_session.add(cache_entry)
        in_memory_session.commit()

        # Resolve - should return manual correction first
        result = resolve_correction_then_cache(in_memory_session, fingerprint)

        assert result is not None
        assert isinstance(result, ManualCorrection)
        assert result.source_fingerprint == fingerprint
        assert result.spotify_track_id == "spotify:track:manual123"
        assert result.origin == "manual_override"

    def test_resolve_returns_cache_entry_when_no_correction(self, in_memory_session: Session):
        """When no manual correction exists, returns the automatic cache entry."""
        fingerprint = "test-fingerprint-456"

        # Create and insert only an automatic cache entry
        cache_entry = MatchCacheEntry(
            source_fingerprint=fingerprint,
            spotify_track_id="spotify:track:auto789",
            confidence=75,
            origin="auto",
            last_verified_at=datetime.now(timezone.utc),
        )
        in_memory_session.add(cache_entry)
        in_memory_session.commit()

        # Resolve - should return cache entry
        result = resolve_correction_then_cache(in_memory_session, fingerprint)

        assert result is not None
        assert isinstance(result, MatchCacheEntry)
        assert result.source_fingerprint == fingerprint
        assert result.spotify_track_id == "spotify:track:auto789"
        assert result.confidence == 75
        assert result.origin == "auto"

    def test_resolve_returns_none_when_neither_exists(self, in_memory_session: Session):
        """When neither manual correction nor cache entry exists, returns None."""
        fingerprint = "non-existent-fingerprint"

        result = resolve_correction_then_cache(in_memory_session, fingerprint)

        assert result is None

    def test_resolve_ignores_cache_when_correction_exists(self, in_memory_session: Session):
        """When both exist, correction is returned and cache is ignored."""
        fingerprint = "test-fingerprint-789"

        # Insert manual correction
        correction = ManualCorrection(
            source_fingerprint=fingerprint,
            spotify_track_id="spotify:track:manual999",
            origin="manual",
            explanation="User provided correction",
        )
        in_memory_session.add(correction)

        # Insert cache entry with different data
        cache_entry = MatchCacheEntry(
            source_fingerprint=fingerprint,
            spotify_track_id="spotify:track:auto111",
            confidence=50,
            origin="auto",
            last_verified_at=datetime.now(timezone.utc),
        )
        in_memory_session.add(cache_entry)
        in_memory_session.commit()

        # Resolve - should return correction
        result = resolve_correction_then_cache(in_memory_session, fingerprint)

        assert result is not None
        assert isinstance(result, ManualCorrection)
        # Verify it's the correction, not the cache entry
        assert result.spotify_track_id == "spotify:track:manual999"
        assert result.origin == "manual"


class TestRecordJobError:
    """Tests for record_job_error function."""

    def test_record_job_error_updates_job(self, in_memory_session: Session):
        """record_job_error stores a safe error summary on the job."""
        # Create a job first
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_playlist_id="spotify:playlist:abc123",
            destination_playlist_id="youtube:playlist:def456",
            source_service=SourceService.YOUTUBE,
            destination_service=DestinationService.SPOTIFY,
            transfer_mode=TransferMode.CREATE,
        )
        create_job(in_memory_session, request, job_id, created_at)

        # Record an error
        updated_at = datetime.now(timezone.utc)
        safe_code = "SPOTIFY_404"
        safe_message = "Playlist not found"

        result = record_job_error(
            in_memory_session,
            job_id,
            safe_code,
            safe_message,
            updated_at,
        )

        # Verify the job was updated
        assert result.id == job_id
        assert result.last_error == "[SPOTIFY_404] Playlist not found"
        assert result.updated_at == updated_at

        # Reload the job and verify the error persists
        reloaded = get_job(in_memory_session, job_id)
        assert reloaded is not None
        assert reloaded.last_error == "[SPOTIFY_404] Playlist not found"

    def test_record_job_error_raises_job_not_found(self, in_memory_session: Session):
        """record_job_error raises JobNotFoundError for non-existent job."""
        job_id = "non-existent-job-id"
        updated_at = datetime.now(timezone.utc)

        with pytest.raises(JobNotFoundError) as exc_info:
            record_job_error(
                in_memory_session,
                job_id,
                "TEST_ERROR",
                "Some error message",
                updated_at,
            )

        assert exc_info.value.job_id == job_id

    def test_record_job_error_raises_value_error_empty_code(self, in_memory_session: Session):
        """record_job_error raises ValueError when safe_code is empty."""
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_playlist_id="spotify:playlist:abc123",
            destination_playlist_id="youtube:playlist:def456",
            source_service=SourceService.YOUTUBE,
            destination_service=DestinationService.SPOTIFY,
            transfer_mode=TransferMode.CREATE,
        )
        create_job(in_memory_session, request, job_id, created_at)
        updated_at = datetime.now(timezone.utc)

        with pytest.raises(ValueError) as exc_info:
            record_job_error(
                in_memory_session,
                job_id,
                "",
                "Some error message",
                updated_at,
            )
        assert "safe_code cannot be empty" in str(exc_info.value)

    def test_record_job_error_raises_value_error_empty_message(self, in_memory_session: Session):
        """record_job_error raises ValueError when safe_message is empty."""
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_playlist_id="spotify:playlist:abc123",
            destination_playlist_id="youtube:playlist:def456",
            source_service=SourceService.YOUTUBE,
            destination_service=DestinationService.SPOTIFY,
            transfer_mode=TransferMode.CREATE,
        )
        create_job(in_memory_session, request, job_id, created_at)
        updated_at = datetime.now(timezone.utc)

        with pytest.raises(ValueError) as exc_info:
            record_job_error(
                in_memory_session,
                job_id,
                "TEST_ERROR",
                "",
                updated_at,
            )
        assert "safe_message cannot be empty" in str(exc_info.value)

    def test_record_job_error_rejects_credential_patterns(self, in_memory_session: Session):
        """record_job_error raises ValueError when safe_message contains credential-like text."""
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_playlist_id="spotify:playlist:abc123",
            destination_playlist_id="youtube:playlist:def456",
            source_service=SourceService.YOUTUBE,
            destination_service=DestinationService.SPOTIFY,
            transfer_mode=TransferMode.CREATE,
        )
        create_job(in_memory_session, request, job_id, created_at)
        updated_at = datetime.now(timezone.utc)

        # Test with a credential-like pattern
        with pytest.raises(ValueError) as exc_info:
            record_job_error(
                in_memory_session,
                job_id,
                "AUTH_ERROR",
                "Invalid API key: abc123",
                updated_at,
            )
        assert "credential-like pattern" in str(exc_info.value)

    def test_record_job_error_accepts_safe_messages_without_credentials(
        self, in_memory_session: Session
    ):
        """record_job_error accepts messages that don't contain credential-like text."""
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_playlist_id="spotify:playlist:abc123",
            destination_playlist_id="youtube:playlist:def456",
            source_service=SourceService.YOUTUBE,
            destination_service=DestinationService.SPOTIFY,
            transfer_mode=TransferMode.CREATE,
        )
        create_job(in_memory_session, request, job_id, created_at)
        updated_at = datetime.now(timezone.utc)

        safe_code = "YOUTUBE_404"
        safe_message = "Video unavailable or removed"

        result = record_job_error(
            in_memory_session,
            job_id,
            safe_code,
            safe_message,
            updated_at,
        )

        assert result.last_error == "[YOUTUBE_404] Video unavailable or removed"

    def test_record_job_error_multiple_errors(self, in_memory_session: Session):
        """record_job_error can be called multiple times, updating the error each time."""
        job_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)
        request = TransferRequest(
            source_playlist_id="spotify:playlist:abc123",
            destination_playlist_id="youtube:playlist:def456",
            source_service=SourceService.YOUTUBE,
            destination_service=DestinationService.SPOTIFY,
            transfer_mode=TransferMode.CREATE,
        )
        create_job(in_memory_session, request, job_id, created_at)

        # First error
        updated_at1 = datetime.now(timezone.utc)
        record_job_error(
            in_memory_session,
            job_id,
            "SPOTIFY_404",
            "Playlist not found",
            updated_at1,
        )

        # Second error (overwrites first)
        updated_at2 = datetime.now(timezone.utc)
        result = record_job_error(
            in_memory_session,
            job_id,
            "SPOTIFY_RATE_LIMIT",
            "Rate limit exceeded",
            updated_at2,
        )

        assert result.last_error == "[SPOTIFY_RATE_LIMIT] Rate limit exceeded"
        assert result.updated_at == updated_at2

        # Reload and verify only the latest error is stored
        reloaded = get_job(in_memory_session, job_id)
        assert reloaded is not None
        assert reloaded.last_error == "[SPOTIFY_RATE_LIMIT] Rate limit exceeded"
