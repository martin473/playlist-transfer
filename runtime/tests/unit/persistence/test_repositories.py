"""Unit tests for repository functions."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.models import MatchCacheEntry
from playlist_bridge.persistence.repositories import lookup_match_cache


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
