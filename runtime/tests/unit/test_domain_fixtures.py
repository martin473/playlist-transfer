"""Tests for domain model fixtures."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from playlist_bridge.domain.models import (
    MatchDecision,
    NormalizedTrackHint,
    SpotifyCandidate,
)


FIXTURES_PATH = Path(__file__).parent.parent / "fixtures" / "domain" / "models.json"


class TestDomainFixtures:
    """Test that domain fixtures validate and serialize correctly."""

    def test_ordinary_song_fixture(self) -> None:
        """Test that the ordinary song fixture validates."""
        with open(FIXTURES_PATH, "r") as f:
            data = json.load(f)

        ordinary_song_data = data["ordinary_song"]
        hint = NormalizedTrackHint(**ordinary_song_data)

        assert hint.source_item_id == "video_ordinary_001"
        assert hint.normalized_title == "Bohemian Rhapsody"
        assert hint.normalized_artist == "Queen"
        assert hint.classification == "song"
        assert hint.version_tokens == ()
        assert hint.unwanted_flags == ()
        assert hint.artist_hints == ("Queen",)

        # Test serialization round-trip
        serialized = hint.model_dump()
        reconstructed = NormalizedTrackHint(**serialized)
        assert reconstructed == hint

    def test_unavailable_video_fixture(self) -> None:
        """Test that the unavailable video fixture validates."""
        with open(FIXTURES_PATH, "r") as f:
            data = json.load(f)

        unavailable_data = data["unavailable_video"]
        hint = NormalizedTrackHint(**unavailable_data)

        assert hint.source_item_id == "video_unavailable_001"
        assert hint.normalized_title == "Unavailable Video"
        assert hint.normalized_artist == "Unknown Artist"
        assert hint.classification == "unknown"
        assert hint.version_tokens == ()
        assert hint.unwanted_flags == ("unavailable",)
        assert hint.artist_hints == ("Unknown Artist",)

        # Test serialization round-trip
        serialized = hint.model_dump()
        reconstructed = NormalizedTrackHint(**serialized)
        assert reconstructed == hint

    def test_spotify_candidate_fixture(self) -> None:
        """Test that the Spotify candidate fixture validates."""
        with open(FIXTURES_PATH, "r") as f:
            data = json.load(f)

        candidate_data = data["spotify_candidate"]
        candidate = SpotifyCandidate(**candidate_data)

        assert candidate.track_id == "6rqhFgbbKwnb9MLmUQDhG6"
        assert candidate.uri == "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
        assert candidate.title == "Bohemian Rhapsody"
        assert candidate.artist_names == ["Queen"]
        assert candidate.album == "A Night at the Opera"
        assert candidate.duration_seconds == 354
        assert candidate.explicit is False
        assert candidate.isrc == "GBUM71029604"
        assert candidate.market_availability == ["US", "GB", "DE"]

        # Test serialization round-trip
        serialized = candidate.model_dump()
        reconstructed = SpotifyCandidate(**serialized)
        assert reconstructed == candidate

    def test_ambiguous_match_fixture(self) -> None:
        """Test that the ambiguous match fixture validates."""
        with open(FIXTURES_PATH, "r") as f:
            data = json.load(f)

        ambiguous_data = data["ambiguous_match"]

        # Validate the source hint
        hint_data = {
            "source_item_id": ambiguous_data["source_item_id"],
            "normalized_title": ambiguous_data["normalized_title"],
            "normalized_artist": ambiguous_data["normalized_artist"],
            "classification": ambiguous_data["classification"],
            "version_tokens": ambiguous_data["version_tokens"],
            "unwanted_flags": ambiguous_data["unwanted_flags"],
            "artist_hints": ambiguous_data["artist_hints"],
        }
        hint = NormalizedTrackHint(**hint_data)

        assert hint.source_item_id == "video_ambiguous_001"
        assert hint.normalized_title == "Bohemian Rhapsody (Live)"
        assert hint.normalized_artist == "Queen"
        assert hint.classification == "song"
        assert hint.version_tokens == ("live",)
        assert hint.unwanted_flags == ()
        assert hint.artist_hints == ("Queen",)

        # Validate alternatives as MatchDecision objects
        alternatives = ambiguous_data["alternatives"]
        assert len(alternatives) == 2

        decision1 = MatchDecision(**alternatives[0])
        assert decision1.source_item_id == "video_ambiguous_001"
        assert decision1.status == "matched"
        assert decision1.selected_candidate is not None
        assert decision1.selected_candidate.track_id == "6rqhFgbbKwnb9MLmUQDhG6"
        assert decision1.selected_candidate.uri == "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
        assert decision1.selected_candidate.title == "Bohemian Rhapsody"
        assert decision1.selected_candidate.artist_names == ["Queen"]
        assert decision1.score is not None
        assert decision1.score.total_score == 0.85
        assert decision1.reason == "High confidence match"

        decision2 = MatchDecision(**alternatives[1])
        assert decision2.source_item_id == "video_ambiguous_001"
        assert decision2.status == "matched"
        assert decision2.selected_candidate is not None
        assert decision2.selected_candidate.track_id == "7yRq6c1J8vL3Z6xS3KxgYk"
        assert decision2.selected_candidate.uri == "spotify:track:7yRq6c1J8vL3Z6xS3KxgYk"
        assert decision2.selected_candidate.title == "Bohemian Rhapsody (Live)"
        assert decision2.selected_candidate.artist_names == ["Queen"]
        assert decision2.score is not None
        assert decision2.score.total_score == 0.45
        assert decision2.reason == "Low confidence match - review required"

        # Test that the hint serializes correctly
        serialized = hint.model_dump()
        reconstructed = NormalizedTrackHint(**serialized)
        assert reconstructed == hint

    def test_fixture_file_exists(self) -> None:
        """Test that the fixtures file exists."""
        assert FIXTURES_PATH.exists()

    def test_fixture_file_is_valid_json(self) -> None:
        """Test that the fixtures file is valid JSON."""
        with open(FIXTURES_PATH, "r") as f:
            data = json.load(f)

        assert "ordinary_song" in data
        assert "unavailable_video" in data
        assert "spotify_candidate" in data
        assert "ambiguous_match" in data
