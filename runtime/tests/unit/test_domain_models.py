"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError

from playlist_bridge.domain.models import MatchDecision, MatchScore, SpotifyCandidate, SourcePlaylistMetadata


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
        # The validator raises ValueError with a specific message
        assert any("status must be one of" in err.get("msg", "").lower() for err in errors)

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


class TestTransferRequest:
    """Tests for the TransferRequest model."""

    def test_create_valid_request(self) -> None:
        """Test creating a valid TransferRequest with all fields."""
        from playlist_bridge.domain.enums import MatchPolicy, TransferMode
        from playlist_bridge.domain.models import TransferRequest

        request = TransferRequest(
            source_url="https://www.youtube.com/playlist?list=PL123",
            source_profile="youtube_user",
            spotify_profile="spotify_user",
            destination_name="My Playlist",
            mode=TransferMode.CREATE,
            match_policy=MatchPolicy.STRICT,
            public=True,
        )

        assert request.source_url == "https://www.youtube.com/playlist?list=PL123"
        assert request.source_profile == "youtube_user"
        assert request.spotify_profile == "spotify_user"
        assert request.destination_name == "My Playlist"
        assert request.mode == TransferMode.CREATE
        assert request.match_policy == MatchPolicy.STRICT
        assert request.public is True

    def test_default_values(self) -> None:
        """Test that default values are applied correctly."""
        from playlist_bridge.domain.enums import MatchPolicy, TransferMode
        from playlist_bridge.domain.models import TransferRequest

        request = TransferRequest(
            source_url="https://www.youtube.com/playlist?list=PL123",
            source_profile="youtube_user",
            spotify_profile="spotify_user",
            destination_name="My Playlist",
        )

        assert request.mode == TransferMode.DRY_RUN
        assert request.match_policy == MatchPolicy.BALANCED
        assert request.public is False

    def test_blank_source_url_is_rejected(self) -> None:
        """Test that a blank source_url is rejected."""
        from playlist_bridge.domain.models import TransferRequest

        with pytest.raises(ValidationError) as exc_info:
            TransferRequest(
                source_url="",
                source_profile="youtube_user",
                spotify_profile="spotify_user",
                destination_name="My Playlist",
            )

        errors = exc_info.value.errors()
        assert any("source_url cannot be empty" in err.get("msg", "") for err in errors)

    def test_blank_source_profile_is_rejected(self) -> None:
        """Test that a blank source_profile is rejected."""
        from playlist_bridge.domain.models import TransferRequest

        with pytest.raises(ValidationError) as exc_info:
            TransferRequest(
                source_url="https://www.youtube.com/playlist?list=PL123",
                source_profile="",
                spotify_profile="spotify_user",
                destination_name="My Playlist",
            )

        errors = exc_info.value.errors()
        assert any("source_profile cannot be empty" in err.get("msg", "") for err in errors)

    def test_blank_spotify_profile_is_rejected(self) -> None:
        """Test that a blank spotify_profile is rejected."""
        from playlist_bridge.domain.models import TransferRequest

        with pytest.raises(ValidationError) as exc_info:
            TransferRequest(
                source_url="https://www.youtube.com/playlist?list=PL123",
                source_profile="youtube_user",
                spotify_profile="",
                destination_name="My Playlist",
            )

        errors = exc_info.value.errors()
        assert any("spotify_profile cannot be empty" in err.get("msg", "") for err in errors)

    def test_blank_destination_name_is_rejected(self) -> None:
        """Test that a blank destination_name is rejected."""
        from playlist_bridge.domain.models import TransferRequest

        with pytest.raises(ValidationError) as exc_info:
            TransferRequest(
                source_url="https://www.youtube.com/playlist?list=PL123",
                source_profile="youtube_user",
                spotify_profile="spotify_user",
                destination_name="",
            )

        errors = exc_info.value.errors()
        assert any("destination_name cannot be empty" in err.get("msg", "") for err in errors)

    def test_whitespace_only_values_are_rejected(self) -> None:
        """Test that whitespace-only values are rejected."""
        from playlist_bridge.domain.models import TransferRequest

        with pytest.raises(ValidationError) as exc_info:
            TransferRequest(
                source_url="   ",
                source_profile="   ",
                spotify_profile="   ",
                destination_name="   ",
            )

        errors = exc_info.value.errors()
        # The field validators catch the first violation
        assert any("source_url cannot be empty" in err.get("msg", "") for err in errors)

    def test_request_round_trip_serialization(self) -> None:
        """Test that TransferRequest round-trips through serialization."""
        from playlist_bridge.domain.enums import MatchPolicy, TransferMode
        from playlist_bridge.domain.models import TransferRequest

        original = TransferRequest(
            source_url="https://www.youtube.com/playlist?list=PL123",
            source_profile="youtube_user",
            spotify_profile="spotify_user",
            destination_name="My Playlist",
            mode=TransferMode.REPLACE,
            match_policy=MatchPolicy.LOOSE,
            public=False,
        )

        data = original.model_dump()
        reconstructed = TransferRequest(**data)

        assert reconstructed.source_url == original.source_url
        assert reconstructed.source_profile == original.source_profile
        assert reconstructed.spotify_profile == original.spotify_profile
        assert reconstructed.destination_name == original.destination_name
        assert reconstructed.mode == original.mode
        assert reconstructed.match_policy == original.match_policy
        assert reconstructed.public == original.public

    def test_unknown_fields_are_rejected(self) -> None:
        """Test that unknown fields are rejected by the model."""
        from playlist_bridge.domain.models import TransferRequest

        with pytest.raises(ValidationError) as exc_info:
            TransferRequest(
                source_url="https://www.youtube.com/playlist?list=PL123",
                source_profile="youtube_user",
                spotify_profile="spotify_user",
                destination_name="My Playlist",
                destination_profile="extra",  # Unknown field
                policy="loose",  # Unknown field
                visibility="public",  # Unknown field
            )

        # Pydantic will reject unknown fields
        errors = exc_info.value.errors()
        # Check that at least one error mentions an unknown field
        assert any("Extra inputs are not permitted" in err.get("msg", "") for err in errors)


class TestTransferResult:
    """Tests for the TransferResult model."""

    def test_create_valid_result(self) -> None:
        """Test creating a valid TransferResult."""
        from playlist_bridge.domain.models import TransferResult

        result = TransferResult(
            job_id="job_123",
            status="completed",
            counts={"total": 50, "matched": 48, "unmatched": 2},
            destination_id="spotify:playlist:abc123",
            report_paths=["reports/job_123.json"],
        )

        assert result.job_id == "job_123"
        assert result.status == "completed"
        assert result.counts == {"total": 50, "matched": 48, "unmatched": 2}
        assert result.destination_id == "spotify:playlist:abc123"
        assert result.report_paths == ["reports/job_123.json"]

    def test_result_without_destination_id(self) -> None:
        """Test that destination_id can be omitted."""
        from playlist_bridge.domain.models import TransferResult

        result = TransferResult(
            job_id="job_456",
            status="failed",
            counts={"total": 10, "matched": 0, "unmatched": 10},
            report_paths=["reports/job_456.json"],
        )

        assert result.job_id == "job_456"
        assert result.status == "failed"
        assert result.counts == {"total": 10, "matched": 0, "unmatched": 10}
        assert result.destination_id is None
        assert result.report_paths == ["reports/job_456.json"]

    def test_result_without_report_paths(self) -> None:
        """Test that report_paths defaults to empty list."""
        from playlist_bridge.domain.models import TransferResult

        result = TransferResult(
            job_id="job_789",
            status="completed",
            counts={"total": 0, "matched": 0, "unmatched": 0},
        )

        assert result.job_id == "job_789"
        assert result.status == "completed"
        assert result.counts == {"total": 0, "matched": 0, "unmatched": 0}
        assert result.destination_id is None
        assert result.report_paths == []

    def test_empty_job_id_is_rejected(self) -> None:
        """Test that an empty job_id is rejected."""
        from playlist_bridge.domain.models import TransferResult

        with pytest.raises(ValidationError) as exc_info:
            TransferResult(
                job_id="",
                status="completed",
                counts={"total": 0},
            )

        errors = exc_info.value.errors()
        assert any("job_id cannot be empty" in err.get("msg", "") for err in errors)

    def test_empty_status_is_rejected(self) -> None:
        """Test that an empty status is rejected."""
        from playlist_bridge.domain.models import TransferResult

        with pytest.raises(ValidationError) as exc_info:
            TransferResult(
                job_id="job_123",
                status="",
                counts={"total": 0},
            )

        errors = exc_info.value.errors()
        assert any("status cannot be empty" in err.get("msg", "") for err in errors)

    def test_blank_job_id_is_rejected(self) -> None:
        """Test that a blank job_id (whitespace only) is rejected."""
        from playlist_bridge.domain.models import TransferResult

        with pytest.raises(ValidationError) as exc_info:
            TransferResult(
                job_id="   ",
                status="completed",
                counts={"total": 0},
            )

        errors = exc_info.value.errors()
        assert any("job_id cannot be empty" in err.get("msg", "") for err in errors)

    def test_blank_status_is_rejected(self) -> None:
        """Test that a blank status (whitespace only) is rejected."""
        from playlist_bridge.domain.models import TransferResult

        with pytest.raises(ValidationError) as exc_info:
            TransferResult(
                job_id="job_123",
                status="   ",
                counts={"total": 0},
            )

        errors = exc_info.value.errors()
        assert any("status cannot be empty" in err.get("msg", "") for err in errors)

    def test_result_round_trip_serialization(self) -> None:
        """Test that TransferResult round-trips through serialization."""
        from playlist_bridge.domain.models import TransferResult

        original = TransferResult(
            job_id="job_abc",
            status="completed",
            counts={"total": 100, "matched": 95, "unmatched": 5, "failed": 0},
            destination_id="spotify:playlist:xyz789",
            report_paths=["reports/job_abc.json", "reports/job_abc_matches.csv"],
        )

        data = original.model_dump()
        reconstructed = TransferResult(**data)

        assert reconstructed.job_id == original.job_id
        assert reconstructed.status == original.status
        assert reconstructed.counts == original.counts
        assert reconstructed.destination_id == original.destination_id
        assert reconstructed.report_paths == original.report_paths

    def test_unknown_fields_are_rejected_for_result(self) -> None:
        """Test that unknown fields are rejected by TransferResult."""
        from playlist_bridge.domain.models import TransferResult

        with pytest.raises(ValidationError) as exc_info:
            TransferResult(
                job_id="job_123",
                status="completed",
                counts={"total": 0},
                extra_field="not_allowed",
            )

        errors = exc_info.value.errors()
        assert any("Extra inputs are not permitted" in err.get("msg", "") for err in errors)


class TestVerificationResult:
    """Tests for the VerificationResult model."""

    def test_exact_match_result(self) -> None:
        """Test creating an exact match verification result."""
        from playlist_bridge.domain.models import VerificationResult

        expected = ["spotify:track:abc123", "spotify:track:def456", "spotify:track:ghi789"]
        actual = ["spotify:track:abc123", "spotify:track:def456", "spotify:track:ghi789"]

        result = VerificationResult(
            is_exact_match=True,
            missing_positions=[],
            extra_positions=[],
            reordered_positions=[],
            unavailable_positions=[],
            expected_items=expected,
            actual_items=actual,
        )

        assert result.is_exact_match is True
        assert result.missing_positions == []
        assert result.extra_positions == []
        assert result.reordered_positions == []
        assert result.unavailable_positions == []
        assert result.expected_items == expected
        assert result.actual_items == actual

    def test_mismatch_result_missing_items(self) -> None:
        """Test creating a mismatch result with missing items."""
        from playlist_bridge.domain.models import VerificationResult

        expected = ["spotify:track:abc123", "spotify:track:def456", "spotify:track:ghi789"]
        actual = ["spotify:track:abc123", "spotify:track:ghi789"]  # Missing def456

        result = VerificationResult(
            is_exact_match=False,
            missing_positions=[1],
            extra_positions=[],
            reordered_positions=[],
            unavailable_positions=[],
            expected_items=expected,
            actual_items=actual,
        )

        assert result.is_exact_match is False
        assert result.missing_positions == [1]
        assert result.extra_positions == []
        assert result.reordered_positions == []
        assert result.unavailable_positions == []
        assert result.expected_items == expected
        assert result.actual_items == actual

    def test_mismatch_result_extra_items(self) -> None:
        """Test creating a mismatch result with extra items."""
        from playlist_bridge.domain.models import VerificationResult

        expected = ["spotify:track:abc123", "spotify:track:def456"]
        actual = ["spotify:track:abc123", "spotify:track:def456", "spotify:track:extra999"]

        result = VerificationResult(
            is_exact_match=False,
            missing_positions=[],
            extra_positions=[2],
            reordered_positions=[],
            unavailable_positions=[],
            expected_items=expected,
            actual_items=actual,
        )

        assert result.is_exact_match is False
        assert result.missing_positions == []
        assert result.extra_positions == [2]
        assert result.reordered_positions == []
        assert result.unavailable_positions == []

    def test_mismatch_result_unavailable_items(self) -> None:
        """Test creating a mismatch result with unavailable items."""
        from playlist_bridge.domain.models import VerificationResult

        expected = ["spotify:track:abc123", "spotify:track:def456", "spotify:track:ghi789"]
        actual = ["spotify:track:abc123", None, "spotify:track:ghi789"]

        result = VerificationResult(
            is_exact_match=False,
            missing_positions=[],
            extra_positions=[],
            reordered_positions=[],
            unavailable_positions=[1],
            expected_items=expected,
            actual_items=actual,
        )

        assert result.is_exact_match is False
        assert result.missing_positions == []
        assert result.extra_positions == []
        assert result.reordered_positions == []
        assert result.unavailable_positions == [1]
        assert result.actual_items[1] is None

    def test_mismatch_result_reordered_items(self) -> None:
        """Test creating a mismatch result with reordered items."""
        from playlist_bridge.domain.models import VerificationResult

        expected = ["spotify:track:abc123", "spotify:track:def456", "spotify:track:ghi789"]
        actual = ["spotify:track:abc123", "spotify:track:ghi789", "spotify:track:def456"]

        result = VerificationResult(
            is_exact_match=False,
            missing_positions=[],
            extra_positions=[],
            reordered_positions=[1, 2],
            unavailable_positions=[],
            expected_items=expected,
            actual_items=actual,
        )

        assert result.is_exact_match is False
        assert result.missing_positions == []
        assert result.extra_positions == []
        assert result.reordered_positions == [1, 2]
        assert result.unavailable_positions == []

    def test_inconsistent_exact_match_raises_error(self) -> None:
        """Test that inconsistent exact match state raises validation error."""
        from playlist_bridge.domain.models import VerificationResult

        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                is_exact_match=True,
                missing_positions=[1],  # Should be empty if exact match
                extra_positions=[],
                reordered_positions=[],
                unavailable_positions=[],
                expected_items=["spotify:track:abc123"],
                actual_items=["spotify:track:abc123"],
            )

        # Check that the validation error was raised with the expected message
        # The error may be in the 'msg' field or in the 'ctx' field
        found = False
        for error in exc_info.value.errors():
            if "is_exact_match True but has mismatch details" in str(error):
                found = True
                break
            if error.get("ctx") and isinstance(error["ctx"], dict):
                ctx_error = error["ctx"].get("error")
                if ctx_error and "is_exact_match True but has mismatch details" in str(ctx_error):
                    found = True
                    break
        assert found, f"Expected error message not found in {exc_info.value.errors()}"

    def test_inconsistent_mismatch_raises_error(self) -> None:
        """Test that inconsistent mismatch state raises validation error."""
        from playlist_bridge.domain.models import VerificationResult

        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                is_exact_match=False,
                missing_positions=[],
                extra_positions=[],
                reordered_positions=[],
                unavailable_positions=[],  # Should have at least one mismatch detail
                expected_items=["spotify:track:abc123"],
                actual_items=["spotify:track:abc123"],
            )

        # Check that the validation error was raised with the expected message
        # The error may be in the 'msg' field or in the 'ctx' field
        found = False
        for error in exc_info.value.errors():
            if "is_exact_match False but no mismatch details" in str(error):
                found = True
                break
            if error.get("ctx") and isinstance(error["ctx"], dict):
                ctx_error = error["ctx"].get("error")
                if ctx_error and "is_exact_match False but no mismatch details" in str(ctx_error):
                    found = True
                    break
        assert found, f"Expected error message not found in {exc_info.value.errors()}"

    def test_negative_positions_are_rejected(self) -> None:
        """Test that negative positions are rejected."""
        from playlist_bridge.domain.models import VerificationResult

        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                is_exact_match=False,
                missing_positions=[-1],
                extra_positions=[],
                reordered_positions=[],
                unavailable_positions=[],
                expected_items=["spotify:track:abc123"],
                actual_items=[],
            )

        errors = exc_info.value.errors()
        assert any("Positions must be non-negative" in err.get("msg", "") for err in errors)

    def test_out_of_range_positions_are_rejected(self) -> None:
        """Test that positions out of range are rejected."""
        from playlist_bridge.domain.models import VerificationResult

        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                is_exact_match=False,
                missing_positions=[5],  # Out of range
                extra_positions=[],
                reordered_positions=[],
                unavailable_positions=[],
                expected_items=["spotify:track:abc123"],  # Only 1 item
                actual_items=[],
            )

        errors = exc_info.value.errors()
        assert any("missing_positions index out of range" in err.get("msg", "") for err in errors)

    def test_empty_expected_items_are_rejected(self) -> None:
        """Test that empty expected_items list is rejected."""
        from playlist_bridge.domain.models import VerificationResult

        with pytest.raises(ValidationError) as exc_info:
            VerificationResult(
                is_exact_match=True,
                missing_positions=[],
                extra_positions=[],
                reordered_positions=[],
                unavailable_positions=[],
                expected_items=[],  # Empty
                actual_items=[],
            )

        errors = exc_info.value.errors()
        assert any("expected_items cannot be empty" in err.get("msg", "") for err in errors)

    def test_verification_result_round_trip(self) -> None:
        """Test that VerificationResult round-trips through serialization."""
        from playlist_bridge.domain.models import VerificationResult

        original = VerificationResult(
            is_exact_match=False,
            missing_positions=[1],  # Position 1 is missing (expected 'b')
            extra_positions=[3],    # Position 3 is extra ('y')
            reordered_positions=[2],  # Position 2 is reordered ('c' moved)
            unavailable_positions=[0],  # Position 0 is unavailable
            expected_items=["spotify:track:a", "spotify:track:b", "spotify:track:c"],
            actual_items=[None, "spotify:track:x", "spotify:track:a", "spotify:track:y"],
        )

        data = original.model_dump()
        reconstructed = VerificationResult(**data)

        assert reconstructed.is_exact_match == original.is_exact_match
        assert reconstructed.missing_positions == original.missing_positions
        assert reconstructed.extra_positions == original.extra_positions
        assert reconstructed.reordered_positions == original.reordered_positions
        assert reconstructed.unavailable_positions == original.unavailable_positions
        assert reconstructed.expected_items == original.expected_items
        assert reconstructed.actual_items == original.actual_items


class TestDestinationPlaylist:
    """Tests for the DestinationPlaylist model."""

    def test_create_valid_destination_playlist(self) -> None:
        """Test creating a valid DestinationPlaylist."""
        from playlist_bridge.domain.models import DestinationPlaylist

        playlist = DestinationPlaylist(
            playlist_id="spotify:playlist:xyz789",
            name="My Awesome Playlist",
            owner_id="user123",
            public=True,
            collaborative=False,
            description="A collection of great songs",
            snapshot_id="snapshot_abc123",
            external_url="https://open.spotify.com/playlist/xyz789",
            track_count=50,
        )

        assert playlist.playlist_id == "spotify:playlist:xyz789"
        assert playlist.name == "My Awesome Playlist"
        assert playlist.owner_id == "user123"
        assert playlist.public is True
        assert playlist.collaborative is False
        assert playlist.description == "A collection of great songs"
        assert playlist.snapshot_id == "snapshot_abc123"
        assert playlist.external_url == "https://open.spotify.com/playlist/xyz789"
        assert playlist.track_count == 50

    def test_destination_playlist_minimal_fields(self) -> None:
        """Test creating a DestinationPlaylist with only required fields."""
        from playlist_bridge.domain.models import DestinationPlaylist

        playlist = DestinationPlaylist(
            playlist_id="spotify:playlist:abc123",
            name="Minimal Playlist",
            owner_id="user456",
            public=False,
            collaborative=False,
            track_count=0,
        )

        assert playlist.playlist_id == "spotify:playlist:abc123"
        assert playlist.name == "Minimal Playlist"
        assert playlist.owner_id == "user456"
        assert playlist.public is False
        assert playlist.collaborative is False
        assert playlist.description is None
        assert playlist.snapshot_id is None
        assert playlist.external_url is None
        assert playlist.track_count == 0

    def test_destination_playlist_empty_id_rejected(self) -> None:
        """Test that an empty playlist_id is rejected."""
        from playlist_bridge.domain.models import DestinationPlaylist

        with pytest.raises(ValidationError) as exc_info:
            DestinationPlaylist(
                playlist_id="",
                name="Test Playlist",
                owner_id="user123",
                public=True,
                collaborative=False,
                track_count=10,
            )

        errors = exc_info.value.errors()
        assert any("playlist_id cannot be empty" in err.get("msg", "") for err in errors)

    def test_destination_playlist_empty_name_rejected(self) -> None:
        """Test that an empty name is rejected."""
        from playlist_bridge.domain.models import DestinationPlaylist

        with pytest.raises(ValidationError) as exc_info:
            DestinationPlaylist(
                playlist_id="spotify:playlist:abc123",
                name="",
                owner_id="user123",
                public=True,
                collaborative=False,
                track_count=10,
            )

        errors = exc_info.value.errors()
        assert any("name cannot be empty" in err.get("msg", "") for err in errors)

    def test_destination_playlist_negative_track_count_rejected(self) -> None:
        """Test that a negative track_count is rejected."""
        from playlist_bridge.domain.models import DestinationPlaylist

        with pytest.raises(ValidationError) as exc_info:
            DestinationPlaylist(
                playlist_id="spotify:playlist:abc123",
                name="Test Playlist",
                owner_id="user123",
                public=True,
                collaborative=False,
                track_count=-1,
            )

        errors = exc_info.value.errors()
        # The validation is from Pydantic's ge constraint
        assert any("Input should be greater than or equal to 0" in err.get("msg", "") for err in errors)

    def test_destination_playlist_unknown_fields_rejected(self) -> None:
        """Test that unknown fields are rejected by DestinationPlaylist."""
        from playlist_bridge.domain.models import DestinationPlaylist

        with pytest.raises(ValidationError) as exc_info:
            DestinationPlaylist(
                playlist_id="spotify:playlist:abc123",
                name="Test Playlist",
                owner_id="user123",
                public=True,
                collaborative=False,
                track_count=10,
                extra_field="not_allowed",
            )

        errors = exc_info.value.errors()
        assert any("Extra inputs are not permitted" in err.get("msg", "") for err in errors)

    def test_destination_playlist_round_trip(self) -> None:
        """Test that DestinationPlaylist round-trips through serialization."""
        from playlist_bridge.domain.models import DestinationPlaylist

        original = DestinationPlaylist(
            playlist_id="spotify:playlist:xyz789",
            name="My Awesome Playlist",
            owner_id="user123",
            public=True,
            collaborative=True,
            description="A collection of great songs",
            snapshot_id="snapshot_abc123",
            external_url="https://open.spotify.com/playlist/xyz789",
            track_count=50,
        )

        data = original.model_dump()
        reconstructed = DestinationPlaylist(**data)

        assert reconstructed.playlist_id == original.playlist_id
        assert reconstructed.name == original.name
        assert reconstructed.owner_id == original.owner_id
        assert reconstructed.public == original.public
        assert reconstructed.collaborative == original.collaborative
        assert reconstructed.description == original.description
        assert reconstructed.snapshot_id == original.snapshot_id
        assert reconstructed.external_url == original.external_url
        assert reconstructed.track_count == original.track_count


class TestSourcePlaylistMetadata:
    """Tests for the SourcePlaylistMetadata model."""

    def test_create_valid_source_metadata(self) -> None:
        """Test creating a valid SourcePlaylistMetadata."""
        from playlist_bridge.domain.models import SourcePlaylistMetadata

        metadata = SourcePlaylistMetadata(
            reference="https://www.youtube.com/playlist?list=PL123456789",
            description="A great collection of songs",
            privacy_status="public",
            owner_channel_id="UC123456789",
            owner_channel_title="Awesome Music Channel",
            item_count=42,
        )

        assert metadata.reference == "https://www.youtube.com/playlist?list=PL123456789"
        assert metadata.description == "A great collection of songs"
        assert metadata.privacy_status == "public"
        assert metadata.owner_channel_id == "UC123456789"
        assert metadata.owner_channel_title == "Awesome Music Channel"
        assert metadata.item_count == 42

    def test_source_metadata_minimal_fields(self) -> None:
        """Test creating a SourcePlaylistMetadata with only required fields."""
        from playlist_bridge.domain.models import SourcePlaylistMetadata

        metadata = SourcePlaylistMetadata(
            reference="https://www.youtube.com/playlist?list=PL456789012",
            item_count=0,
        )

        assert metadata.reference == "https://www.youtube.com/playlist?list=PL456789012"
        assert metadata.description is None
        assert metadata.privacy_status is None
        assert metadata.owner_channel_id is None
        assert metadata.owner_channel_title is None
        assert metadata.item_count == 0

    def test_source_metadata_empty_reference_rejected(self) -> None:
        """Test that an empty reference is rejected."""
        from playlist_bridge.domain.models import SourcePlaylistMetadata

        with pytest.raises(ValidationError) as exc_info:
            SourcePlaylistMetadata(
                reference="",
                item_count=10,
            )

        errors = exc_info.value.errors()
        assert any("reference cannot be empty" in err.get("msg", "") for err in errors)

    def test_source_metadata_negative_item_count_rejected(self) -> None:
        """Test that a negative item_count is rejected."""
        from playlist_bridge.domain.models import SourcePlaylistMetadata

        with pytest.raises(ValidationError) as exc_info:
            SourcePlaylistMetadata(
                reference="https://www.youtube.com/playlist?list=PL123456789",
                item_count=-1,
            )

        errors = exc_info.value.errors()
        # The validation is from Pydantic's ge constraint
        assert any("Input should be greater than or equal to 0" in err.get("msg", "") for err in errors)

    def test_source_metadata_unknown_fields_rejected(self) -> None:
        """Test that unknown fields are rejected by SourcePlaylistMetadata."""
        from playlist_bridge.domain.models import SourcePlaylistMetadata

        with pytest.raises(ValidationError) as exc_info:
            SourcePlaylistMetadata(
                reference="https://www.youtube.com/playlist?list=PL123456789",
                item_count=10,
                extra_field="not_allowed",
            )

        errors = exc_info.value.errors()
        assert any("Extra inputs are not permitted" in err.get("msg", "") for err in errors)

    def test_source_metadata_round_trip(self) -> None:
        """Test that SourcePlaylistMetadata round-trips through serialization."""
        from playlist_bridge.domain.models import SourcePlaylistMetadata

        original = SourcePlaylistMetadata(
            reference="https://www.youtube.com/playlist?list=PL123456789",
            description="A great collection of songs",
            privacy_status="public",
            owner_channel_id="UC123456789",
            owner_channel_title="Awesome Music Channel",
            item_count=42,
        )

        data = original.model_dump()
        reconstructed = SourcePlaylistMetadata(**data)

        assert reconstructed.reference == original.reference
        assert reconstructed.description == original.description
        assert reconstructed.privacy_status == original.privacy_status
        assert reconstructed.owner_channel_id == original.owner_channel_id
        assert reconstructed.owner_channel_title == original.owner_channel_title
        assert reconstructed.item_count == original.item_count
