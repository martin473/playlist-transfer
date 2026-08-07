"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError

from playlist_bridge.domain.models import SpotifyCandidate


class TestSpotifyCandidate:
    """Tests for the SpotifyCandidate model."""

    def test_create_valid_candidate(self) -> None:
        """Test creating a valid SpotifyCandidate."""
        candidate = SpotifyCandidate(
            track_id="6rqhFgbbKwnb9MLmUQDhG6",
            uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
            title="Bohemian Rhapsody",
            artist_names=["Queen"],
            album="A Night at the Opera",
            duration_seconds=354,
            explicit=False,
            isrc="GBUM71029604",
            market_availability=["US", "GB", "DE"],
        )

        assert candidate.track_id == "6rqhFgbbKwnb9MLmUQDhG6"
        assert candidate.uri == "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
        assert candidate.title == "Bohemian Rhapsody"
        assert candidate.artist_names == ["Queen"]
        assert candidate.album == "A Night at the Opera"
        assert candidate.duration_seconds == 354
        assert candidate.explicit is False
        assert candidate.isrc == "GBUM71029604"
        assert candidate.market_availability == ["US", "GB", "DE"]

    def test_candidate_without_uri_is_rejected(self) -> None:
        """Test that a candidate without a Spotify URI is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="6rqhFgbbKwnb9MLmUQDhG6",
                uri="invalid-uri",  # Invalid URI format
                title="Bohemian Rhapsody",
                artist_names=["Queen"],
                album="A Night at the Opera",
                duration_seconds=354,
                explicit=False,
            )

        # Verify the validation error is about the URI
        errors = exc_info.value.errors()
        assert any("URI must start with 'spotify:track:'" in err.get("msg", "") for err in errors)

    def test_candidate_with_empty_uri_is_rejected(self) -> None:
        """Test that a candidate with an empty URI is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="6rqhFgbbKwnb9MLmUQDhG6",
                uri="",  # Empty URI
                title="Bohemian Rhapsody",
                artist_names=["Queen"],
                album="A Night at the Opera",
                duration_seconds=354,
                explicit=False,
            )

        errors = exc_info.value.errors()
        assert any("URI must start with 'spotify:track:'" in err.get("msg", "") for err in errors)

    def test_candidate_without_track_id_is_rejected(self) -> None:
        """Test that a candidate without a track ID is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="",  # Empty track ID
                uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
                title="Bohemian Rhapsody",
                artist_names=["Queen"],
                album="A Night at the Opera",
                duration_seconds=354,
                explicit=False,
            )

        errors = exc_info.value.errors()
        assert any("Track ID cannot be empty" in err.get("msg", "") for err in errors)

    def test_candidate_without_title_is_rejected(self) -> None:
        """Test that a candidate without a title is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="6rqhFgbbKwnb9MLmUQDhG6",
                uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
                title="",  # Empty title
                artist_names=["Queen"],
                album="A Night at the Opera",
                duration_seconds=354,
                explicit=False,
            )

        errors = exc_info.value.errors()
        assert any("Title cannot be empty" in err.get("msg", "") for err in errors)

    def test_candidate_without_artist_names_is_rejected(self) -> None:
        """Test that a candidate without artist names is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="6rqhFgbbKwnb9MLmUQDhG6",
                uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
                title="Bohemian Rhapsody",
                artist_names=[],  # Empty artist list
                album="A Night at the Opera",
                duration_seconds=354,
                explicit=False,
            )

        errors = exc_info.value.errors()
        assert any("Artist names cannot be empty" in err.get("msg", "") for err in errors)

    def test_candidate_without_album_is_rejected(self) -> None:
        """Test that a candidate without an album is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="6rqhFgbbKwnb9MLmUQDhG6",
                uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
                title="Bohemian Rhapsody",
                artist_names=["Queen"],
                album="",  # Empty album
                duration_seconds=354,
                explicit=False,
            )

        errors = exc_info.value.errors()
        assert any("Album cannot be empty" in err.get("msg", "") for err in errors)

    def test_candidate_with_negative_duration_is_rejected(self) -> None:
        """Test that a candidate with negative duration is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            SpotifyCandidate(
                track_id="6rqhFgbbKwnb9MLmUQDhG6",
                uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
                title="Bohemian Rhapsody",
                artist_names=["Queen"],
                album="A Night at the Opera",
                duration_seconds=-1,  # Invalid duration
                explicit=False,
            )

        errors = exc_info.value.errors()
        assert any("Input should be greater than or equal to 0" in err.get("msg", "") for err in errors)

    def test_candidate_with_optional_fields_omitted(self) -> None:
        """Test creating a candidate with optional fields omitted."""
        candidate = SpotifyCandidate(
            track_id="6rqhFgbbKwnb9MLmUQDhG6",
            uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
            title="Bohemian Rhapsody",
            artist_names=["Queen"],
            album="A Night at the Opera",
            duration_seconds=354,
            explicit=False,
        )

        assert candidate.isrc is None
        assert candidate.market_availability is None

    def test_candidate_with_multiple_artists(self) -> None:
        """Test creating a candidate with multiple artists."""
        candidate = SpotifyCandidate(
            track_id="6rqhFgbbKwnb9MLmUQDhG6",
            uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
            title="Under Pressure",
            artist_names=["Queen", "David Bowie"],
            album="Hot Space",
            duration_seconds=242,
            explicit=False,
        )

        assert candidate.artist_names == ["Queen", "David Bowie"]

    def test_candidate_serialization(self) -> None:
        """Test that the candidate can be serialized to dict."""
        candidate = SpotifyCandidate(
            track_id="6rqhFgbbKwnb9MLmUQDhG6",
            uri="spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
            title="Bohemian Rhapsody",
            artist_names=["Queen"],
            album="A Night at the Opera",
            duration_seconds=354,
            explicit=False,
            isrc="GBUM71029604",
            market_availability=["US", "GB"],
        )

        data = candidate.model_dump()
        assert data["track_id"] == "6rqhFgbbKwnb9MLmUQDhG6"
        assert data["uri"] == "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
        assert data["title"] == "Bohemian Rhapsody"
        assert data["artist_names"] == ["Queen"]
        assert data["album"] == "A Night at the Opera"
        assert data["duration_seconds"] == 354
        assert data["explicit"] is False
        assert data["isrc"] == "GBUM71029604"
        assert data["market_availability"] == ["US", "GB"]
