"""Unit tests for persistence models."""

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import JobRecord, AccountProfileRecord, MatchCacheEntry, ManualCorrection


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


def test_match_cache_entry_round_trip(session):
    """Test that a match cache entry can be created, saved, and reloaded."""
    # Create a match cache entry
    now = datetime.now(timezone.utc)
    original = MatchCacheEntry(
        source_fingerprint="fp_abc123",
        spotify_track_id="spotify:track:xyz789",
        confidence=95,
        origin="automatic",
        last_verified_at=now,
        created_at=now,
        updated_at=now,
    )

    # Save to database
    session.add(original)
    session.commit()

    # Reload from database
    reloaded = session.get(MatchCacheEntry, original.id)
    assert reloaded is not None

    # Verify all fields round-trip unchanged
    assert reloaded.id == original.id
    assert reloaded.source_fingerprint == original.source_fingerprint
    assert reloaded.spotify_track_id == original.spotify_track_id
    assert reloaded.confidence == original.confidence
    assert reloaded.origin == original.origin
    assert reloaded.last_verified_at == original.last_verified_at
    assert reloaded.created_at == original.created_at
    assert reloaded.updated_at == original.updated_at


def test_match_cache_entry_fingerprint_unique(session):
    """Test that inserting the same source_fingerprint twice raises an integrity error."""
    # Insert first entry
    now = datetime.now(timezone.utc)
    entry1 = MatchCacheEntry(
        source_fingerprint="fp_unique123",
        spotify_track_id="spotify:track:abc123",
        confidence=80,
        origin="manual",
        last_verified_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(entry1)
    session.commit()

    # Attempt to insert second entry with same fingerprint
    entry2 = MatchCacheEntry(
        source_fingerprint="fp_unique123",
        spotify_track_id="spotify:track:def456",
        confidence=90,
        origin="manual",
        last_verified_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(entry2)

    # Should raise an integrity error due to unique constraint
    with pytest.raises(Exception) as excinfo:
        session.commit()

    # Verify the error is related to the unique constraint
    assert "UNIQUE" in str(excinfo.value) or "IntegrityError" in str(excinfo.value)


def test_match_cache_entry_indexed_lookup(session):
    """Test that match cache entries support indexed lookup by fingerprint."""
    # Insert multiple entries
    now = datetime.now(timezone.utc)
    entries = [
        MatchCacheEntry(
            source_fingerprint=f"fp_{i}",
            spotify_track_id=f"spotify:track:track_{i}",
            confidence=50 + i,
            origin="automatic",
            last_verified_at=now,
            created_at=now,
            updated_at=now,
        )
        for i in range(5)
    ]
    for entry in entries:
        session.add(entry)
    session.commit()

    # Look up by fingerprint
    result = session.query(MatchCacheEntry).filter_by(source_fingerprint="fp_2").first()
    assert result is not None
    assert result.spotify_track_id == "spotify:track:track_2"
    assert result.confidence == 52

    # Look up by spotify track id
    result = session.query(MatchCacheEntry).filter_by(spotify_track_id="spotify:track:track_3").first()
    assert result is not None
    assert result.source_fingerprint == "fp_3"


def test_match_cache_entry_defaults(session):
    """Test that match cache entries correctly set default values."""
    now = datetime.now(timezone.utc)
    entry = MatchCacheEntry(
        source_fingerprint="fp_default_test",
        spotify_track_id="spotify:track:default_test",
        last_verified_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(entry)
    session.commit()

    reloaded = session.get(MatchCacheEntry, entry.id)
    assert reloaded is not None
    assert reloaded.confidence == 0
    assert reloaded.origin == "manual"


def test_manual_correction_round_trip(session):
    """Test that a manual correction can be created, saved, and reloaded."""
    # Create a manual correction with spotify_track_id
    now = datetime.now(timezone.utc)
    original = ManualCorrection(
        source_fingerprint="fp_correct_001",
        spotify_track_id="spotify:track:correct_001",
        skip_reason=None,
        explanation="User confirmed this match",
        origin="manual",
        created_at=now,
        updated_at=now,
    )

    # Save to database
    session.add(original)
    session.commit()

    # Reload from database
    reloaded = session.get(ManualCorrection, original.id)
    assert reloaded is not None

    # Verify all fields round-trip unchanged
    assert reloaded.id == original.id
    assert reloaded.source_fingerprint == original.source_fingerprint
    assert reloaded.spotify_track_id == original.spotify_track_id
    assert reloaded.skip_reason == original.skip_reason
    assert reloaded.explanation == original.explanation
    assert reloaded.origin == original.origin
    assert reloaded.created_at == original.created_at
    assert reloaded.updated_at == original.updated_at


def test_manual_correction_skip(session):
    """Test that a manual correction can represent a skip decision."""
    now = datetime.now(timezone.utc)
    correction = ManualCorrection(
        source_fingerprint="fp_skip_001",
        spotify_track_id=None,
        skip_reason="not_available",
        explanation="User marked as unavailable",
        origin="manual",
        created_at=now,
        updated_at=now,
    )

    session.add(correction)
    session.commit()

    reloaded = session.get(ManualCorrection, correction.id)
    assert reloaded is not None
    assert reloaded.spotify_track_id is None
    assert reloaded.skip_reason == "not_available"
    assert reloaded.explanation == "User marked as unavailable"


def test_manual_correction_replaces_prior_correction(session):
    """Test that a newer correction replaces the prior correction for the same fingerprint.

    This verifies the key acceptance criterion: when two corrections exist for the same
    source_fingerprint, only the most recent one should be considered active.

    Implementation approach: Because the source_fingerprint has a unique constraint,
    we simulate replacement by updating the existing record rather than inserting a new one.
    """
    fingerprint = "fp_replacement_001"
    now = datetime.now(timezone.utc)

    # Create initial correction
    old_correction = ManualCorrection(
        source_fingerprint=fingerprint,
        spotify_track_id="spotify:track:old_001",
        skip_reason=None,
        explanation="Initial correction",
        origin="manual",
        created_at=now,
        updated_at=now,
    )
    session.add(old_correction)
    session.commit()

    # Save the ID of the old correction
    old_id = old_correction.id

    # Retrieve the existing correction and update it (simulating replacement)
    existing = session.query(ManualCorrection).filter_by(source_fingerprint=fingerprint).first()
    assert existing is not None
    existing.spotify_track_id = "spotify:track:new_001"
    existing.explanation = "Updated correction"
    existing.updated_at = datetime.now(timezone.utc)
    session.commit()

    # Query by fingerprint - should return the updated correction
    result = session.query(ManualCorrection).filter_by(source_fingerprint=fingerprint).first()
    assert result is not None
    assert result.id == old_id  # Same record, updated
    assert result.spotify_track_id == "spotify:track:new_001"
    assert result.explanation == "Updated correction"

    # Verify there is only one record for this fingerprint
    count = session.query(ManualCorrection).filter_by(source_fingerprint=fingerprint).count()
    assert count == 1


def test_manual_correction_unique_fingerprint_constraint(session):
    """Test that the unique constraint on source_fingerprint prevents duplicates."""
    now = datetime.now(timezone.utc)

    # Insert first correction
    correction1 = ManualCorrection(
        source_fingerprint="fp_unique_001",
        spotify_track_id="spotify:track:unique_001",
        skip_reason=None,
        explanation="First correction",
        origin="manual",
        created_at=now,
        updated_at=now,
    )
    session.add(correction1)
    session.commit()

    # Attempt to insert second correction with same fingerprint
    correction2 = ManualCorrection(
        source_fingerprint="fp_unique_001",
        spotify_track_id="spotify:track:unique_002",
        skip_reason=None,
        explanation="Second correction",
        origin="manual",
        created_at=now,
        updated_at=now,
    )
    session.add(correction2)

    # Should raise integrity error due to unique constraint
    with pytest.raises(Exception) as excinfo:
        session.commit()

    assert "UNIQUE" in str(excinfo.value) or "IntegrityError" in str(excinfo.value)


def test_manual_correction_default_origin(session):
    """Test that manual corrections default to origin='manual'."""
    now = datetime.now(timezone.utc)
    correction = ManualCorrection(
        source_fingerprint="fp_default_origin",
        spotify_track_id="spotify:track:default_origin",
        skip_reason=None,
        explanation="Test default origin",
        created_at=now,
        updated_at=now,
    )
    session.add(correction)
    session.commit()

    reloaded = session.get(ManualCorrection, correction.id)
    assert reloaded is not None
    assert reloaded.origin == "manual"
