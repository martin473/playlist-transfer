"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError

from playlist_bridge.domain.models import MatchDecision, MatchScore, SpotifyCandidate


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


class TestMatchScore:
    """Tests for the MatchScore model."""

    def test_create_valid_match_score(self) -> None:
        """Test creating a valid MatchScore with all fields."""
        from playlist_bridge.domain.models import MatchScore

        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.90,
            duration_similarity=0.85,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.94,
            reasons=["Title is almost identical", "Artists match exactly"],
        )

        assert score.title_similarity == 0.95
        assert score.artist_similarity == 0.90
        assert score.duration_similarity == 0.85
        assert score.version_agreement == 1.0
        assert score.unwanted_version_penalty == 0.0
        assert score.explicit_state == 1.0
        assert score.total_score == 0.94
        assert score.reasons == ["Title is almost identical", "Artists match exactly"]

    def test_match_score_without_reasons(self) -> None:
        """Test creating a MatchScore without reasons (should use default empty list)."""
        from playlist_bridge.domain.models import MatchScore

        score = MatchScore(
            title_similarity=0.5,
            artist_similarity=0.5,
            duration_similarity=0.5,
            version_agreement=0.5,
            unwanted_version_penalty=0.5,
            explicit_state=0.5,
            total_score=0.5,
        )

        assert score.reasons == []

    def test_match_score_scores_are_constrained_to_zero_to_one(self) -> None:
        """Test that all score fields are constrained to the [0.0, 1.0] range."""
        from playlist_bridge.domain.models import MatchScore

        # Valid values at boundaries
        score = MatchScore(
            title_similarity=0.0,
            artist_similarity=1.0,
            duration_similarity=0.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.0,
        )

        assert score.title_similarity == 0.0
        assert score.artist_similarity == 1.0
        assert score.duration_similarity == 0.0
        assert score.version_agreement == 1.0
        assert score.unwanted_version_penalty == 0.0
        assert score.explicit_state == 1.0
        assert score.total_score == 0.0

    def test_match_score_rejects_values_below_zero(self) -> None:
        """Test that MatchScore rejects values below 0.0."""
        from playlist_bridge.domain.models import MatchScore

        with pytest.raises(ValidationError) as exc_info:
            MatchScore(
                title_similarity=-0.1,
                artist_similarity=0.5,
                duration_similarity=0.5,
                version_agreement=0.5,
                unwanted_version_penalty=0.5,
                explicit_state=0.5,
                total_score=0.5,
            )

        errors = exc_info.value.errors()
        assert any(
            "Input should be greater than or equal to 0" in err.get("msg", "")
            for err in errors
        )

    def test_match_score_rejects_values_above_one(self) -> None:
        """Test that MatchScore rejects values above 1.0."""
        from playlist_bridge.domain.models import MatchScore

        with pytest.raises(ValidationError) as exc_info:
            MatchScore(
                title_similarity=1.1,
                artist_similarity=0.5,
                duration_similarity=0.5,
                version_agreement=0.5,
                unwanted_version_penalty=0.5,
                explicit_state=0.5,
                total_score=0.5,
            )

        errors = exc_info.value.errors()
        assert any(
            "Input should be less than or equal to 1" in err.get("msg", "")
            for err in errors
        )

    def test_match_score_validates_reasons_not_empty_strings(self) -> None:
        """Test that MatchScore rejects reasons that are empty or whitespace-only strings."""
        from playlist_bridge.domain.models import MatchScore

        with pytest.raises(ValidationError) as exc_info:
            MatchScore(
                title_similarity=0.5,
                artist_similarity=0.5,
                duration_similarity=0.5,
                version_agreement=0.5,
                unwanted_version_penalty=0.5,
                explicit_state=0.5,
                total_score=0.5,
                reasons=["Valid reason", "", "   "],
            )

        errors = exc_info.value.errors()
        assert any(
            "Reason strings cannot be empty or whitespace only" in err.get("msg", "")
            for err in errors
        )

    def test_match_score_serialization(self) -> None:
        """Test that MatchScore can be serialized to dict."""
        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.90,
            duration_similarity=0.85,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.94,
            reasons=["Title is almost identical"],
        )

        data = score.model_dump()
        assert data["title_similarity"] == 0.95
        assert data["artist_similarity"] == 0.90
        assert data["duration_similarity"] == 0.85
        assert data["version_agreement"] == 1.0
        assert data["unwanted_version_penalty"] == 0.0
        assert data["explicit_state"] == 1.0
        assert data["total_score"] == 0.94
        assert data["reasons"] == ["Title is almost identical"]


class TestMatchDecision:
    """Tests for the MatchDecision model."""

    def test_matched_decision_requires_candidate_and_score(self) -> None:
        """Test that a matched decision must have a selected candidate and score."""
        candidate = SpotifyCandidate(
            track_id="123",
            uri="spotify:track:123",
            title="Test Track",
            artist_names=["Test Artist"],
            album="Test Album",
            duration_seconds=180,
            explicit=False,
        )
        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.90,
            duration_similarity=0.85,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.94,
            reasons=["Title is almost identical"],
        )

        decision = MatchDecision(
            source_item_id="source-1",
            status="matched",
            selected_candidate=candidate,
            score=score,
            reason="Good match",
        )

        assert decision.source_item_id == "source-1"
        assert decision.status == "matched"
        assert decision.selected_candidate == candidate
        assert decision.score == score
        assert decision.reason == "Good match"
        assert decision.ranked_alternatives == []

    def test_unmatched_decision_has_no_candidate_or_score(self) -> None:
        """Test that an unmatched decision has no selected candidate or score."""
        decision = MatchDecision(
            source_item_id="source-2",
            status="unmatched",
            reason="No suitable candidate found",
        )

        assert decision.source_item_id == "source-2"
        assert decision.status == "unmatched"
        assert decision.selected_candidate is None
        assert decision.score is None
        assert decision.reason == "No suitable candidate found"
        assert decision.ranked_alternatives == []

    def test_matched_decision_without_candidate_is_rejected(self) -> None:
        """Test that a matched decision without a selected candidate is rejected."""
        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.90,
            duration_similarity=0.85,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.94,
            reasons=["Title is almost identical"],
        )

        with pytest.raises(ValidationError) as exc_info:
            MatchDecision(
                source_item_id="source-1",
                status="matched",
                selected_candidate=None,
                score=score,
                reason="Good match",
            )

        errors = exc_info.value.errors()
        assert any("Matched decision must have a selected candidate" in err.get("msg", "") for err in errors)

    def test_matched_decision_without_score_is_rejected(self) -> None:
        """Test that a matched decision without a score is rejected."""
        candidate = SpotifyCandidate(
            track_id="123",
            uri="spotify:track:123",
            title="Test Track",
            artist_names=["Test Artist"],
            album="Test Album",
            duration_seconds=180,
            explicit=False,
        )

        with pytest.raises(ValidationError) as exc_info:
            MatchDecision(
                source_item_id="source-1",
                status="matched",
                selected_candidate=candidate,
                score=None,
                reason="Good match",
            )

        errors = exc_info.value.errors()
        assert any("Matched decision must have a score" in err.get("msg", "") for err in errors)

    def test_unmatched_decision_with_candidate_is_rejected(self) -> None:
        """Test that an unmatched decision with a selected candidate is rejected."""
        candidate = SpotifyCandidate(
            track_id="123",
            uri="spotify:track:123",
            title="Test Track",
            artist_names=["Test Artist"],
            album="Test Album",
            duration_seconds=180,
            explicit=False,
        )

        with pytest.raises(ValidationError) as exc_info:
            MatchDecision(
                source_item_id="source-2",
                status="unmatched",
                selected_candidate=candidate,
                reason="No suitable candidate found",
            )

        errors = exc_info.value.errors()
        assert any("Unmatched decision must not have a selected candidate" in err.get("msg", "") for err in errors)

    def test_unmatched_decision_with_score_is_rejected(self) -> None:
        """Test that an unmatched decision with a score is rejected."""
        score = MatchScore(
            title_similarity=0.5,
            artist_similarity=0.5,
            duration_similarity=0.5,
            version_agreement=0.5,
            unwanted_version_penalty=0.5,
            explicit_state=0.5,
            total_score=0.5,
            reasons=["Low similarity"],
        )

        with pytest.raises(ValidationError) as exc_info:
            MatchDecision(
                source_item_id="source-2",
                status="unmatched",
                score=score,
                reason="No suitable candidate found",
            )

        errors = exc_info.value.errors()
        assert any("Unmatched decision must not have a score" in err.get("msg", "") for err in errors)

    def test_decision_with_invalid_status_is_rejected(self) -> None:
        """Test that a decision with an invalid status is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MatchDecision(
                source_item_id="source-1",
                status="pending",
                reason="Pending review",
            )

        errors = exc_info.value.errors()
        assert any("Status must be one of" in err.get("msg", "") for err in errors)

    def test_decision_with_empty_reason_is_rejected(self) -> None:
        """Test that a decision with an empty reason is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MatchDecision(
                source_item_id="source-1",
                status="unmatched",
                reason="",
            )

        errors = exc_info.value.errors()
        assert any("Reason cannot be empty" in err.get("msg", "") for err in errors)

    def test_decision_with_ranked_alternatives(self) -> None:
        """Test that a decision can have ranked alternatives."""
        candidate1 = SpotifyCandidate(
            track_id="123",
            uri="spotify:track:123",
            title="Best Match",
            artist_names=["Artist A"],
            album="Album A",
            duration_seconds=180,
            explicit=False,
        )
        candidate2 = SpotifyCandidate(
            track_id="456",
            uri="spotify:track:456",
            title="Second Best",
            artist_names=["Artist B"],
            album="Album B",
            duration_seconds=185,
            explicit=True,
        )
        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.90,
            duration_similarity=0.85,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.94,
            reasons=["Title is almost identical"],
        )

        decision = MatchDecision(
            source_item_id="source-1",
            status="matched",
            selected_candidate=candidate1,
            ranked_alternatives=[candidate2],
            score=score,
            reason="Best match found",
        )

        assert decision.ranked_alternatives == [candidate2]

    def test_decision_serialization(self) -> None:
        """Test that MatchDecision can be serialized to dict."""
        candidate = SpotifyCandidate(
            track_id="123",
            uri="spotify:track:123",
            title="Test Track",
            artist_names=["Test Artist"],
            album="Test Album",
            duration_seconds=180,
            explicit=False,
        )
        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.90,
            duration_similarity=0.85,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.94,
            reasons=["Title is almost identical"],
        )

        decision = MatchDecision(
            source_item_id="source-1",
            status="matched",
            selected_candidate=candidate,
            score=score,
            reason="Good match",
            ranked_alternatives=[],
        )

        data = decision.model_dump()
        assert data["source_item_id"] == "source-1"
        assert data["status"] == "matched"
        assert data["selected_candidate"]["track_id"] == "123"
        assert data["score"]["total_score"] == 0.94
        assert data["reason"] == "Good match"
        assert data["ranked_alternatives"] == []
