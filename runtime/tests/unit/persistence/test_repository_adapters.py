"""Unit tests for SQLAlchemy repository adapters."""

from datetime import datetime, timezone
from typing import Sequence

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import Session, sessionmaker

from playlist_bridge.domain.models import MatchDecision, MatchScore, SpotifyCandidate
from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import (
    JobRecord,
    ManualCorrection,
    MatchCacheEntry,
    MatchDecisionRecord,
)
from playlist_bridge.persistence.repositories import (
    JobNotFoundError,
    SqlAlchemyManualCorrectionRepository,
    SqlAlchemyMatchCacheRepository,
    SqlAlchemyMatchDecisionRepository,
    create_job,
    lookup_match_cache,
    lookup_manual_correction,
    upsert_manual_correction,
    upsert_match_cache,
    upsert_match_decision,
)
from playlist_bridge.ports import IntegrityError


@pytest.fixture
def in_memory_session_factory():
    """Create an in-memory SQLite session factory for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal


@pytest.fixture
def in_memory_session(in_memory_session_factory):
    """Create an in-memory SQLite session for testing."""
    with in_memory_session_factory() as session:
        yield session


@pytest.fixture
def sample_job(in_memory_session: Session):
    """Create a sample job for testing."""
    from playlist_bridge.domain.enums import TransferMode, MatchPolicy
    from playlist_bridge.domain.models import TransferRequest
    
    request = TransferRequest(
        source_service="youtube",
        source_playlist_id="PL123",
        destination_service="spotify",
        destination_name="Test Playlist",
        transfer_mode=TransferMode.DRY_RUN,
        match_policy=MatchPolicy.BALANCED,
        dry_run=True,
    )
    job = create_job(
        session=in_memory_session,
        request=request,
        job_id="test-job-123",
        created_at=datetime.now(timezone.utc),
    )
    return job


@pytest.fixture
def sample_spotify_candidate():
    """Create a sample Spotify candidate for testing."""
    return SpotifyCandidate(
        track_id="6rqhFgbbKwnb9MLmUQDhG6",
        uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        title="Test Track",
        artist_names=["Test Artist"],
        album="Test Album",
        duration_seconds=180,
        explicit=False,
    )


@pytest.fixture
def sample_match_score():
    """Create a sample match score for testing."""
    return MatchScore(
        title_similarity=0.9,
        artist_similarity=0.8,
        duration_similarity=0.85,
        version_agreement=1.0,
        unwanted_version_penalty=0.0,
        explicit_state=1.0,
        total_score=0.85,
        reasons=["Good title match", "Good artist match"],
    )


@pytest.fixture
def sample_match_decision(sample_spotify_candidate, sample_match_score):
    """Create a sample match decision for testing."""
    return MatchDecision(
        source_item_id="video_123",
        status="matched",
        selected_candidate=sample_spotify_candidate,
        ranked_alternatives=[],
        score=sample_match_score,
        reason="Good match found",
    )


class TestSqlAlchemyMatchDecisionRepository:
    """Tests for SqlAlchemyMatchDecisionRepository."""

    def test_upsert_creates_new_decision(
        self,
        in_memory_session_factory,
        sample_job,
        sample_match_decision,
    ):
        """Upsert creates a new decision when one doesn't exist."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        result = repo.upsert(sample_job.id, sample_match_decision)

        assert result is sample_match_decision
        # Verify the decision was stored
        with in_memory_session_factory() as session:
            record = session.query(MatchDecisionRecord).filter_by(
                job_id=sample_job.id,
                source_item_id="video_123",
            ).first()
            assert record is not None
            assert record.spotify_track_id == "6rqhFgbbKwnb9MLmUQDhG6"
            assert record.decision_status == "matched"
            assert record.reviewed is False

    def test_upsert_updates_existing_decision(
        self,
        in_memory_session_factory,
        sample_job,
        sample_match_decision,
    ):
        """Upsert updates an existing decision when one exists."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        # First upsert
        repo.upsert(sample_job.id, sample_match_decision)

        # Create a modified decision
        modified_decision = MatchDecision(
            source_item_id="video_123",
            status="unmatched",
            selected_candidate=None,
            ranked_alternatives=[],
            score=None,
            reason="No good match found",
        )

        # Second upsert
        result = repo.upsert(sample_job.id, modified_decision)

        assert result is modified_decision
        # Verify the decision was updated
        with in_memory_session_factory() as session:
            record = session.query(MatchDecisionRecord).filter_by(
                job_id=sample_job.id,
                source_item_id="video_123",
            ).first()
            assert record is not None
            assert record.spotify_track_id is None
            assert record.decision_status == "unmatched"

    def test_upsert_raises_job_not_found(
        self,
        in_memory_session_factory,
        sample_match_decision,
    ):
        """Upsert raises JobNotFoundError when job doesn't exist."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        with pytest.raises(JobNotFoundError) as exc_info:
            repo.upsert("non-existent-job-id", sample_match_decision)

        assert "non-existent-job-id" in str(exc_info.value)

    def test_upsert_raises_value_error_for_empty_job_id(
        self,
        in_memory_session_factory,
        sample_match_decision,
    ):
        """Upsert raises ValueError when job_id is empty."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        with pytest.raises(ValueError) as exc_info:
            repo.upsert("", sample_match_decision)

        assert "job_id cannot be empty" in str(exc_info.value)

    def test_upsert_raises_value_error_for_empty_source_item_id(
        self,
        in_memory_session_factory,
        sample_job,
    ):
        """Upsert raises ValueError when decision has empty source_item_id."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        invalid_decision = MatchDecision(
            source_item_id="",
            status="unmatched",
            selected_candidate=None,
            ranked_alternatives=[],
            score=None,
            reason="No match found",
        )

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(sample_job.id, invalid_decision)

        assert "decision.source_item_id cannot be empty" in str(exc_info.value)

    def test_unresolved_returns_pending_decisions(
        self,
        in_memory_session_factory,
        sample_job,
        sample_match_decision,
    ):
        """unresolved returns decisions with pending/matching/in_review status."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        # Create a matched decision (unresolved)
        repo.upsert(sample_job.id, sample_match_decision)

        # Create an unmatched decision (resolved)
        resolved_decision = MatchDecision(
            source_item_id="video_456",
            status="unmatched",
            selected_candidate=None,
            ranked_alternatives=[],
            score=None,
            reason="No match found",
        )
        # Manually mark as resolved
        with in_memory_session_factory() as session:
            upsert_match_decision(session, sample_job.id, "video_456", resolved_decision)
            # Update the decision_status to "resolved"
            record = session.query(MatchDecisionRecord).filter_by(
                job_id=sample_job.id,
                source_item_id="video_456",
            ).first()
            if record:
                record.decision_status = "resolved"
                session.commit()

        # Get unresolved decisions
        unresolved = repo.unresolved(sample_job.id)

        # Should only return the matched decision (video_123), not the resolved one
        assert len(unresolved) == 1
        assert unresolved[0].source_item_id == "video_123"

    def test_unresolved_returns_empty_list_for_all_resolved(
        self,
        in_memory_session_factory,
        sample_job,
    ):
        """unresolved returns empty list when all decisions are resolved."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        # Create a resolved decision
        resolved_decision = MatchDecision(
            source_item_id="video_789",
            status="unmatched",
            selected_candidate=None,
            ranked_alternatives=[],
            score=None,
            reason="No match found",
        )
        with in_memory_session_factory() as session:
            upsert_match_decision(session, sample_job.id, "video_789", resolved_decision)
            # Update the decision_status to "resolved"
            record = session.query(MatchDecisionRecord).filter_by(
                job_id=sample_job.id,
                source_item_id="video_789",
            ).first()
            if record:
                record.decision_status = "resolved"
                session.commit()

        # Get unresolved decisions
        unresolved = repo.unresolved(sample_job.id)

        # Should return empty list
        assert len(unresolved) == 0

    def test_unresolved_raises_job_not_found(
        self,
        in_memory_session_factory,
    ):
        """unresolved raises JobNotFoundError when job doesn't exist."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        with pytest.raises(JobNotFoundError) as exc_info:
            repo.unresolved("non-existent-job-id")

        assert "non-existent-job-id" in str(exc_info.value)

    def test_unresolved_raises_value_error_for_empty_job_id(
        self,
        in_memory_session_factory,
    ):
        """unresolved raises ValueError when job_id is empty."""
        repo = SqlAlchemyMatchDecisionRepository(in_memory_session_factory)

        with pytest.raises(ValueError) as exc_info:
            repo.unresolved("")

        assert "job_id cannot be empty" in str(exc_info.value)


class TestSqlAlchemyMatchCacheRepository:
    """Tests for SqlAlchemyMatchCacheRepository."""

    def test_get_returns_existing_entry(
        self,
        in_memory_session_factory,
        in_memory_session,
    ):
        """get returns the entry when it exists."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        # Create a cache entry
        entry = MatchCacheEntry(
            source_fingerprint="test-fingerprint-123",
            spotify_track_id="spotify:track:abc123",
            confidence=85,
            origin="manual",
            last_verified_at=datetime.now(timezone.utc),
        )
        upsert_match_cache(in_memory_session, entry)

        # Get the entry
        result = repo.get("test-fingerprint-123")

        assert result is not None
        assert result.source_fingerprint == "test-fingerprint-123"
        assert result.spotify_track_id == "spotify:track:abc123"
        assert result.confidence == 85
        assert result.origin == "manual"

    def test_get_returns_none_for_missing_entry(
        self,
        in_memory_session_factory,
    ):
        """get returns None when entry doesn't exist."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        result = repo.get("non-existent-fingerprint")

        assert result is None

    def test_get_raises_value_error_for_empty_fingerprint(
        self,
        in_memory_session_factory,
    ):
        """get raises ValueError when fingerprint is empty."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        with pytest.raises(ValueError) as exc_info:
            repo.get("")

        assert "fingerprint cannot be empty" in str(exc_info.value)

    def test_upsert_creates_new_entry(
        self,
        in_memory_session_factory,
    ):
        """upsert creates a new entry when one doesn't exist."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        entry = MatchCacheEntry(
            source_fingerprint="test-fingerprint-456",
            spotify_track_id="spotify:track:xyz789",
            confidence=90,
            origin="auto",
            last_verified_at=datetime.now(timezone.utc),
        )

        result = repo.upsert(entry)

        assert result is entry
        # Verify the entry was stored
        with in_memory_session_factory() as session:
            stored = lookup_match_cache(session, "test-fingerprint-456")
            assert stored is not None
            assert stored.spotify_track_id == "spotify:track:xyz789"

    def test_upsert_updates_existing_entry(
        self,
        in_memory_session_factory,
        in_memory_session,
    ):
        """upsert updates an existing entry when one exists."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        # Create initial entry
        initial_entry = MatchCacheEntry(
            source_fingerprint="test-fingerprint-789",
            spotify_track_id="spotify:track:old123",
            confidence=70,
            origin="auto",
            last_verified_at=datetime.now(timezone.utc),
        )
        upsert_match_cache(in_memory_session, initial_entry)

        # Update with new data
        updated_entry = MatchCacheEntry(
            source_fingerprint="test-fingerprint-789",
            spotify_track_id="spotify:track:new456",
            confidence=95,
            origin="manual",
            last_verified_at=datetime.now(timezone.utc),
        )

        result = repo.upsert(updated_entry)

        assert result is updated_entry
        # Verify the entry was updated
        with in_memory_session_factory() as session:
            stored = lookup_match_cache(session, "test-fingerprint-789")
            assert stored is not None
            assert stored.spotify_track_id == "spotify:track:new456"
            assert stored.confidence == 95
            assert stored.origin == "manual"

    def test_upsert_raises_value_error_for_none_entry(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when entry is None."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(None)  # type: ignore

        assert "entry cannot be None" in str(exc_info.value)

    def test_upsert_raises_value_error_for_empty_fingerprint(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when entry has empty source_fingerprint."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        invalid_entry = MatchCacheEntry(
            source_fingerprint="",
            spotify_track_id="spotify:track:abc123",
            confidence=85,
            origin="manual",
            last_verified_at=datetime.now(timezone.utc),
        )

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(invalid_entry)

        assert "entry.source_fingerprint cannot be empty" in str(exc_info.value)

    def test_upsert_raises_value_error_for_empty_spotify_id(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when entry has empty spotify_track_id."""
        repo = SqlAlchemyMatchCacheRepository(in_memory_session_factory)

        invalid_entry = MatchCacheEntry(
            source_fingerprint="test-fingerprint",
            spotify_track_id="",
            confidence=85,
            origin="manual",
            last_verified_at=datetime.now(timezone.utc),
        )

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(invalid_entry)

        assert "entry.spotify_track_id cannot be empty" in str(exc_info.value)


class TestSqlAlchemyManualCorrectionRepository:
    """Tests for SqlAlchemyManualCorrectionRepository."""

    def test_get_returns_existing_correction(
        self,
        in_memory_session_factory,
        in_memory_session,
    ):
        """get returns the correction when it exists."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        # Create a manual correction
        correction = ManualCorrection(
            source_fingerprint="test-fingerprint-123",
            spotify_track_id="spotify:track:abc123",
            skip_reason=None,
            explanation="User verified match",
            origin="manual",
        )
        upsert_manual_correction(in_memory_session, correction)

        # Get the correction
        result = repo.get("test-fingerprint-123")

        assert result is not None
        assert result.source_fingerprint == "test-fingerprint-123"
        assert result.spotify_track_id == "spotify:track:abc123"
        assert result.skip_reason is None
        assert result.explanation == "User verified match"

    def test_get_returns_none_for_missing_correction(
        self,
        in_memory_session_factory,
    ):
        """get returns None when correction doesn't exist."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        result = repo.get("non-existent-fingerprint")

        assert result is None

    def test_get_raises_value_error_for_empty_fingerprint(
        self,
        in_memory_session_factory,
    ):
        """get raises ValueError when fingerprint is empty."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        with pytest.raises(ValueError) as exc_info:
            repo.get("")

        assert "fingerprint cannot be empty" in str(exc_info.value)

    def test_upsert_creates_new_correction_with_spotify_id(
        self,
        in_memory_session_factory,
    ):
        """upsert creates a new correction with spotify_track_id."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        correction = ManualCorrection(
            source_fingerprint="test-fingerprint-456",
            spotify_track_id="spotify:track:xyz789",
            skip_reason=None,
            explanation="User selected correct match",
            origin="manual",
        )

        result = repo.upsert(correction)

        assert result is correction
        # Verify the correction was stored
        with in_memory_session_factory() as session:
            stored = lookup_manual_correction(session, "test-fingerprint-456")
            assert stored is not None
            assert stored.spotify_track_id == "spotify:track:xyz789"
            assert stored.skip_reason is None

    def test_upsert_creates_new_correction_with_skip_reason(
        self,
        in_memory_session_factory,
    ):
        """upsert creates a new correction with skip_reason."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        correction = ManualCorrection(
            source_fingerprint="test-fingerprint-789",
            spotify_track_id=None,
            skip_reason="Not a song",
            explanation="This is a spoken word track",
            origin="manual",
        )

        result = repo.upsert(correction)

        assert result is correction
        # Verify the correction was stored
        with in_memory_session_factory() as session:
            stored = lookup_manual_correction(session, "test-fingerprint-789")
            assert stored is not None
            assert stored.spotify_track_id is None
            assert stored.skip_reason == "Not a song"

    def test_upsert_updates_existing_correction(
        self,
        in_memory_session_factory,
        in_memory_session,
    ):
        """upsert updates an existing correction when one exists."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        # Create initial correction
        initial_correction = ManualCorrection(
            source_fingerprint="test-fingerprint-999",
            spotify_track_id="spotify:track:old123",
            skip_reason=None,
            explanation="Original match",
            origin="manual",
        )
        upsert_manual_correction(in_memory_session, initial_correction)

        # Update with new data
        updated_correction = ManualCorrection(
            source_fingerprint="test-fingerprint-999",
            spotify_track_id="spotify:track:new456",
            skip_reason=None,
            explanation="Better match found",
            origin="manual",
        )

        result = repo.upsert(updated_correction)

        assert result is updated_correction
        # Verify the correction was updated
        with in_memory_session_factory() as session:
            stored = lookup_manual_correction(session, "test-fingerprint-999")
            assert stored is not None
            assert stored.spotify_track_id == "spotify:track:new456"
            assert stored.explanation == "Better match found"

    def test_upsert_raises_value_error_for_none_correction(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when correction is None."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(None)  # type: ignore

        assert "correction cannot be None" in str(exc_info.value)

    def test_upsert_raises_value_error_for_empty_fingerprint(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when correction has empty source_fingerprint."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        invalid_correction = ManualCorrection(
            source_fingerprint="",
            spotify_track_id="spotify:track:abc123",
            skip_reason=None,
            explanation="",
            origin="manual",
        )

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(invalid_correction)

        assert "correction.source_fingerprint cannot be empty" in str(exc_info.value)

    def test_upsert_raises_value_error_when_no_resolution_provided(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when neither spotify_id nor skip_reason is provided."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        invalid_correction = ManualCorrection(
            source_fingerprint="test-fingerprint",
            spotify_track_id=None,
            skip_reason=None,
            explanation="",
            origin="manual",
        )

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(invalid_correction)

        assert "correction must have either spotify_track_id or skip_reason" in str(exc_info.value)

    def test_upsert_raises_value_error_when_both_provided(
        self,
        in_memory_session_factory,
    ):
        """upsert raises ValueError when both spotify_id and skip_reason are provided."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        invalid_correction = ManualCorrection(
            source_fingerprint="test-fingerprint",
            spotify_track_id="spotify:track:abc123",
            skip_reason="Not a song",
            explanation="",
            origin="manual",
        )

        with pytest.raises(ValueError) as exc_info:
            repo.upsert(invalid_correction)

        assert "correction cannot have both spotify_track_id and skip_reason" in str(exc_info.value)

    def test_upsert_with_skip_reason_updates_existing(
        self,
        in_memory_session_factory,
        in_memory_session,
    ):
        """upsert updates an existing correction with a skip reason."""
        repo = SqlAlchemyManualCorrectionRepository(in_memory_session_factory)

        # Create initial correction with spotify_id
        initial_correction = ManualCorrection(
            source_fingerprint="test-fingerprint-555",
            spotify_track_id="spotify:track:old123",
            skip_reason=None,
            explanation="Original match",
            origin="manual",
        )
        upsert_manual_correction(in_memory_session, initial_correction)

        # Update to skip
        updated_correction = ManualCorrection(
            source_fingerprint="test-fingerprint-555",
            spotify_track_id=None,
            skip_reason="User wants to skip",
            explanation="User decided to skip this track",
            origin="manual",
        )

        result = repo.upsert(updated_correction)

        assert result is updated_correction
        # Verify the correction was updated to skip
        with in_memory_session_factory() as session:
            stored = lookup_manual_correction(session, "test-fingerprint-555")
            assert stored is not None
            assert stored.spotify_track_id is None
            assert stored.skip_reason == "User wants to skip"
            assert stored.explanation == "User decided to skip this track"
