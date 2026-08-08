"""Unit tests for persistence models."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import JobRecord, AccountProfileRecord


@pytest.fixture
def session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_job_record_imports():
    """Test that JobRecord imports and can be instantiated."""
    # Just verify the class exists and can be created with minimal fields
    job = JobRecord(
        id="test-id-123",
        request_json={"source": "spotify:playlist:abc", "destination": "youtube"},
        state="pending",
        created_at=datetime.now(timezone.utc),
    )
    assert job.id == "test-id-123"
    assert job.state == "pending"
    assert job.source_playlist_id is None
    assert job.destination_playlist_id is None


def test_job_record_round_trip(session):
    """Test that a job record can be created, saved, and reloaded with all fields intact."""
    # Create a job with all fields set
    created_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    original_job = JobRecord(
        id="job-abc-123",
        request_json={
            "source": "spotify:playlist:source123",
            "destination": "youtube:playlist:dest456",
            "mode": "merge",
            "policy": "balanced",
            "visibility": "public",
        },
        state="processing",
        source_playlist_id="source123",
        destination_playlist_id="dest456",
        source_track_count=42,
        match_checkpoint=10,
        write_checkpoint=5,
        verification_checkpoint=3,
        created_at=created_at,
        updated_at=created_at,
        last_error="No error yet",
        lease_holder="worker-1",
        lease_expires_at=datetime(2026, 1, 1, 13, 0, 0, tzinfo=timezone.utc),
        row_version=2,
    )

    # Save to database
    session.add(original_job)
    session.commit()

    # Reload from database
    reloaded = session.get(JobRecord, "job-abc-123")
    assert reloaded is not None

    # Verify all fields round-trip unchanged
    assert reloaded.id == original_job.id
    assert reloaded.request_json == original_job.request_json
    assert reloaded.state == original_job.state
    assert reloaded.source_playlist_id == original_job.source_playlist_id
    assert reloaded.destination_playlist_id == original_job.destination_playlist_id
    assert reloaded.source_track_count == original_job.source_track_count
    assert reloaded.match_checkpoint == original_job.match_checkpoint
    assert reloaded.write_checkpoint == original_job.write_checkpoint
    assert reloaded.verification_checkpoint == original_job.verification_checkpoint
    assert reloaded.created_at == original_job.created_at
    assert reloaded.updated_at == original_job.updated_at
    assert reloaded.last_error == original_job.last_error
    assert reloaded.lease_holder == original_job.lease_holder
    assert reloaded.lease_expires_at == original_job.lease_expires_at
    assert reloaded.row_version == original_job.row_version


def test_job_record_pending_state_defaults(session):
    """Test that a job can be created with pending state and minimal fields."""
    job = JobRecord(
        id="pending-001",
        request_json={"source": "spotify:playlist:test"},
        state="pending",
        created_at=datetime.now(timezone.utc),
    )
    session.add(job)
    session.commit()

    reloaded = session.get(JobRecord, "pending-001")
    assert reloaded is not None
    assert reloaded.state == "pending"
    assert reloaded.match_checkpoint == 0
    assert reloaded.write_checkpoint == 0
    assert reloaded.verification_checkpoint == 0
    assert reloaded.row_version == 1
    assert reloaded.source_playlist_id is None
    assert reloaded.destination_playlist_id is None


def test_account_profile_record_round_trip(session):
    """Test that an account profile record can be created, saved, and reloaded."""
    # Create an account profile
    created_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    original = AccountProfileRecord(
        service="spotify",
        profile_name="default",
        provider_user_id="spotify-user-123",
        display_name="My Spotify Account",
        created_at=created_at,
        updated_at=created_at,
    )

    # Save to database
    session.add(original)
    session.commit()

    # Reload from database
    reloaded = session.get(AccountProfileRecord, original.id)
    assert reloaded is not None

    # Verify all fields round-trip unchanged
    assert reloaded.id == original.id
    assert reloaded.service == original.service
    assert reloaded.profile_name == original.profile_name
    assert reloaded.provider_user_id == original.provider_user_id
    assert reloaded.display_name == original.display_name
    assert reloaded.created_at == original.created_at
    assert reloaded.updated_at == original.updated_at


def test_account_profile_unique_constraint(session):
    """Test that inserting the same service/profile pair twice raises an integrity error."""
    # Insert first profile
    profile1 = AccountProfileRecord(
        service="spotify",
        profile_name="default",
        provider_user_id="spotify-user-123",
        display_name="My Spotify Account",
        created_at=datetime.now(timezone.utc),
    )
    session.add(profile1)
    session.commit()

    # Attempt to insert second profile with same service and profile_name
    profile2 = AccountProfileRecord(
        service="spotify",
        profile_name="default",
        provider_user_id="spotify-user-456",
        display_name="Another Spotify Account",
        created_at=datetime.now(timezone.utc),
    )
    session.add(profile2)

    # Should raise an integrity error due to unique constraint
    with pytest.raises(Exception) as excinfo:
        session.commit()

    # Verify the error is related to the unique constraint
    # SQLite error message contains "UNIQUE constraint failed"
    assert "UNIQUE" in str(excinfo.value) or "IntegrityError" in str(excinfo.value)


def test_account_profile_different_services_allowed(session):
    """Test that different services with the same profile_name can coexist."""
    # Insert profile for Spotify
    profile1 = AccountProfileRecord(
        service="spotify",
        profile_name="default",
        provider_user_id="spotify-user-123",
        display_name="My Spotify Account",
        created_at=datetime.now(timezone.utc),
    )
    session.add(profile1)
    session.commit()

    # Insert profile for YouTube with same profile_name
    profile2 = AccountProfileRecord(
        service="youtube",
        profile_name="default",
        provider_user_id="youtube-user-456",
        display_name="My YouTube Channel",
        created_at=datetime.now(timezone.utc),
    )
    session.add(profile2)
    session.commit()

    # Both should exist
    spotify_profile = session.query(AccountProfileRecord).filter_by(service="spotify", profile_name="default").first()
    youtube_profile = session.query(AccountProfileRecord).filter_by(service="youtube", profile_name="default").first()
    assert spotify_profile is not None
    assert youtube_profile is not None
    assert spotify_profile.service == "spotify"
    assert youtube_profile.service == "youtube"


def test_account_profile_different_names_allowed(session):
    """Test that different profile_names with the same service can coexist."""
    # Insert first profile
    profile1 = AccountProfileRecord(
        service="spotify",
        profile_name="default",
        provider_user_id="spotify-user-123",
        display_name="My Spotify Account",
        created_at=datetime.now(timezone.utc),
    )
    session.add(profile1)
    session.commit()

    # Insert second profile with different profile_name
    profile2 = AccountProfileRecord(
        service="spotify",
        profile_name="work",
        provider_user_id="spotify-user-456",
        display_name="Work Spotify Account",
        created_at=datetime.now(timezone.utc),
    )
    session.add(profile2)
    session.commit()

    # Both should exist
    default_profile = session.query(AccountProfileRecord).filter_by(service="spotify", profile_name="default").first()
    work_profile = session.query(AccountProfileRecord).filter_by(service="spotify", profile_name="work").first()
    assert default_profile is not None
    assert work_profile is not None
    assert default_profile.profile_name == "default"
    assert work_profile.profile_name == "work"
