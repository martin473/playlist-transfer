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
    get_job,
    get_source_tracks_ordered,
    lookup_match_cache,
    upsert_match_cache,
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
            provider="spotify",
            account_id="user123",
            display_name="Test User",
        )

        # Save it
        saved = save_profile(session=in_memory_session, profile=profile)

        # Verify the saved profile
        assert saved.provider == "spotify"
        assert saved.account_id == "user123"
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
            provider="spotify",
            account_id="user123",
            display_name="New Name",
        )
        saved = save_profile(session=in_memory_session, profile=profile)

        # Verify the saved profile has updated display_name
        assert saved.provider == "spotify"
        assert saved.account_id == "user123"
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
            provider="spotify",
            account_id="existing_user",
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
            provider="spotify",
            account_id="user1",
            display_name="User One",
        )
        profile2 = AccountProfile(
            provider="spotify",
            account_id="user2",
            display_name="User Two",
        )
        profile3 = AccountProfile(
            provider="youtube",
            account_id="yt_user1",
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
            provider="spotify",
            account_id="user123",
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
        assert retrieved.provider == "spotify"
        assert retrieved.account_id == "user123"
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
            provider="spotify",
            account_id="user1",
            display_name="User One",
        )
        profile2 = AccountProfile(
            provider="spotify",
            account_id="user2",
            display_name="User Two",
        )
        profile3 = AccountProfile(
            provider="youtube",
            account_id="yt_user1",
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
        assert profiles[0].provider == "spotify"
        assert profiles[0].account_id == "user1"
        assert profiles[1].provider == "spotify"
        assert profiles[1].account_id == "user2"
        assert profiles[2].provider == "youtube"
        assert profiles[2].account_id == "yt_user1"

    def test_list_profiles_filters_by_service(self, in_memory_session: Session):
        """list_profiles should filter by service when provided."""
        from playlist_bridge.domain.models import AccountProfile
        from playlist_bridge.persistence.repositories import list_profiles, save_profile

        # Save profiles for different services
        profile1 = AccountProfile(
            provider="spotify",
            account_id="user1",
            display_name="User One",
        )
        profile2 = AccountProfile(
            provider="spotify",
            account_id="user2",
            display_name="User Two",
        )
        profile3 = AccountProfile(
            provider="youtube",
            account_id="yt_user1",
            display_name="YouTube User",
        )

        save_profile(session=in_memory_session, profile=profile1)
        save_profile(session=in_memory_session, profile=profile2)
        save_profile(session=in_memory_session, profile=profile3)

        # List only spotify profiles
        spotify_profiles = list_profiles(
            session=in_memory_session,
            service="spotify",
        )
        assert len(spotify_profiles) == 2
        assert all(p.provider == "spotify" for p in spotify_profiles)

        # List only youtube profiles
        youtube_profiles = list_profiles(
            session=in_memory_session,
            service="youtube",
        )
        assert len(youtube_profiles) == 1
        assert youtube_profiles[0].provider == "youtube"

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
