"""Integration tests for resume reconciliation and job stages."""

import pytest

from playlist_bridge.domain.models import (
    SourceTrack,
    MatchDecision,
    MatchScore,
    SpotifyCandidate,
)
from playlist_bridge.jobs.runner import accepted_uris_in_source_order


class TestResumeReconciliation:
    """Integration tests for resume reconciliation flows."""

    def test_accepted_uris_with_full_job_data(self) -> None:
        """Test accepted URIs extraction with realistic job data."""
        # Simulate a job with mixed track statuses
        tracks = [
            SourceTrack(
                position=0,
                title="Track 1 - Available",
                artist_names=["Artist One"],
                duration_seconds=180,
                video_id="vid001",
                availability="available",
            ),
            SourceTrack(
                position=1,
                title="Track 2 - Unavailable",
                artist_names=["Artist Two"],
                duration_seconds=200,
                video_id="vid002",
                availability="unavailable",
            ),
            SourceTrack(
                position=2,
                title="Track 3 - Skipped",
                artist_names=["Artist Three"],
                duration_seconds=190,
                video_id="vid003",
                availability="available",
            ),
            SourceTrack(
                position=3,
                title="Track 4 - Accepted",
                artist_names=["Artist Four"],
                duration_seconds=210,
                video_id="vid004",
                availability="available",
            ),
            SourceTrack(
                position=4,
                title="Track 5 - Unmatched",
                artist_names=["Artist Five"],
                duration_seconds=175,
                video_id="vid005",
                availability="available",
            ),
            SourceTrack(
                position=5,
                title="Track 6 - Review",
                artist_names=["Artist Six"],
                duration_seconds=195,
                video_id="vid006",
                availability="available",
            ),
            SourceTrack(
                position=6,
                title="Track 7 - Accepted Duplicate",
                artist_names=["Artist Four"],
                duration_seconds=210,
                video_id="vid007",
                availability="available",
            ),
        ]

        # Create candidates
        candidate1 = SpotifyCandidate(
            track_id="accepted1",
            uri="spotify:track:accepted1",
            title="Track 1 - Available",
            artist_names=["Artist One"],
            album="Album One",
            duration_seconds=180,
            explicit=False,
        )
        candidate2 = SpotifyCandidate(
            track_id="unavailable",
            uri="spotify:track:unavailable",
            title="Track 2 - Unavailable",
            artist_names=["Artist Two"],
            album="Album Two",
            duration_seconds=200,
            explicit=False,
        )
        candidate3 = SpotifyCandidate(
            track_id="skipped",
            uri="spotify:track:skipped",
            title="Track 3 - Skipped",
            artist_names=["Artist Three"],
            album="Album Three",
            duration_seconds=190,
            explicit=False,
        )
        candidate4 = SpotifyCandidate(
            track_id="accepted2",
            uri="spotify:track:accepted2",
            title="Track 4 - Accepted",
            artist_names=["Artist Four"],
            album="Album Four",
            duration_seconds=210,
            explicit=False,
        )
        candidate5 = SpotifyCandidate(
            track_id="unmatched",
            uri="spotify:track:unmatched",
            title="Track 5 - Unmatched",
            artist_names=["Artist Five"],
            album="Album Five",
            duration_seconds=175,
            explicit=False,
        )
        candidate6 = SpotifyCandidate(
            track_id="review",
            uri="spotify:track:review",
            title="Track 6 - Review",
            artist_names=["Artist Six"],
            album="Album Six",
            duration_seconds=195,
            explicit=False,
        )
        candidate7 = SpotifyCandidate(
            track_id="accepted3",
            uri="spotify:track:accepted3",
            title="Track 7 - Accepted Duplicate",
            artist_names=["Artist Four"],
            album="Album Four",
            duration_seconds=210,
            explicit=False,
        )

        # Create scores
        score1 = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )
        score2 = MatchScore(
            title_similarity=0.0,
            artist_similarity=0.0,
            duration_similarity=0.0,
            version_agreement=0.0,
            unwanted_version_penalty=0.0,
            explicit_state=0.0,
            total_score=0.0,
            reasons=["Unavailable"],
        )
        score3 = MatchScore(
            title_similarity=0.0,
            artist_similarity=0.0,
            duration_similarity=0.0,
            version_agreement=0.0,
            unwanted_version_penalty=0.0,
            explicit_state=0.0,
            total_score=0.0,
            reasons=["Skipped"],
        )
        score4 = MatchScore(
            title_similarity=0.98,
            artist_similarity=0.95,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.98,
            reasons=["Excellent match"],
        )
        score5 = MatchScore(
            title_similarity=0.2,
            artist_similarity=0.2,
            duration_similarity=0.0,
            version_agreement=0.0,
            unwanted_version_penalty=0.0,
            explicit_state=0.0,
            total_score=0.2,
            reasons=["Low confidence"],
        )
        score6 = MatchScore(
            title_similarity=0.6,
            artist_similarity=0.5,
            duration_similarity=0.7,
            version_agreement=0.5,
            unwanted_version_penalty=0.0,
            explicit_state=0.5,
            total_score=0.6,
            reasons=["Needs review"],
        )
        score7 = MatchScore(
            title_similarity=0.92,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.92,
            reasons=["Good match"],
        )

        decisions = [
            MatchDecision(
                source_item_id="vid001",
                status="matched",
                selected_candidate=candidate1,
                score=score1,
                reason="Good match",
            ),
            MatchDecision(
                source_item_id="vid002",
                status="unmatched",
                reason="Track unavailable",
            ),
            MatchDecision(
                source_item_id="vid003",
                status="unmatched",
                reason="Skipped by user",
            ),
            MatchDecision(
                source_item_id="vid004",
                status="matched",
                selected_candidate=candidate4,
                score=score4,
                reason="Excellent match",
            ),
            MatchDecision(
                source_item_id="vid005",
                status="unmatched",
                reason="No suitable match found",
            ),
            MatchDecision(
                source_item_id="vid006",
                status="unmatched",
                reason="Needs manual review",
            ),
            MatchDecision(
                source_item_id="vid007",
                status="matched",
                selected_candidate=candidate7,
                score=score7,
                reason="Good match",
            ),
        ]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only accepted tracks should be included, in source order
        expected = [
            "spotify:track:accepted1",  # Track 1
            "spotify:track:accepted2",  # Track 4
            "spotify:track:accepted3",  # Track 7
        ]
        assert result == expected

    def test_resume_scenario_partial_completion(self) -> None:
        """Test resume scenario where some decisions are already made."""
        # Scenario: A job was partially completed and is being resumed
        tracks = [
            SourceTrack(
                position=0,
                title="Song A",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="a1",
                availability="available",
            ),
            SourceTrack(
                position=1,
                title="Song B",
                artist_names=["Artist B"],
                duration_seconds=200,
                video_id="b2",
                availability="available",
            ),
            SourceTrack(
                position=2,
                title="Song C",
                artist_names=["Artist C"],
                duration_seconds=190,
                video_id="c3",
                availability="available",
            ),
            SourceTrack(
                position=3,
                title="Song D",
                artist_names=["Artist D"],
                duration_seconds=210,
                video_id="d4",
                availability="available",
            ),
        ]

        # Create candidates
        candidate_a = SpotifyCandidate(
            track_id="accepted_a",
            uri="spotify:track:accepted_a",
            title="Song A",
            artist_names=["Artist A"],
            album="Album A",
            duration_seconds=180,
            explicit=False,
        )
        candidate_c = SpotifyCandidate(
            track_id="accepted_c",
            uri="spotify:track:accepted_c",
            title="Song C",
            artist_names=["Artist C"],
            album="Album C",
            duration_seconds=190,
            explicit=False,
        )
        candidate_d = SpotifyCandidate(
            track_id="unmatched_d",
            uri="spotify:track:unmatched_d",
            title="Song D",
            artist_names=["Artist D"],
            album="Album D",
            duration_seconds=210,
            explicit=False,
        )

        # Create scores
        score_a = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )
        score_c = MatchScore(
            title_similarity=0.85,
            artist_similarity=0.8,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.85,
            reasons=["Good match"],
        )
        score_d = MatchScore(
            title_similarity=0.3,
            artist_similarity=0.3,
            duration_similarity=0.2,
            version_agreement=0.0,
            unwanted_version_penalty=0.0,
            explicit_state=0.0,
            total_score=0.3,
            reasons=["Low confidence"],
        )

        decisions = [
            MatchDecision(
                source_item_id="a1",
                status="matched",
                selected_candidate=candidate_a,
                score=score_a,
                reason="Good match",
            ),
            # Song B has no decision yet
            MatchDecision(
                source_item_id="c3",
                status="matched",
                selected_candidate=candidate_c,
                score=score_c,
                reason="Good match",
            ),
            MatchDecision(
                source_item_id="d4",
                status="unmatched",
                reason="No suitable match found",
            ),
        ]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only accepted tracks that have decisions
        expected = [
            "spotify:track:accepted_a",  # Track A - accepted
            # Track B - no decision, skipped
            "spotify:track:accepted_c",  # Track C - accepted
            # Track D - unmatched, skipped
        ]
        assert result == expected

    def test_handles_mixed_decision_types(self) -> None:
        """Test handling of various decision types."""
        track = SourceTrack(
            position=0,
            title="Test Track",
            artist_names=["Test Artist"],
            duration_seconds=180,
            video_id="test123",
            availability="available",
        )

        # Test matched vs unmatched status
        # Matched status with candidate -> included
        candidate = SpotifyCandidate(
            track_id="accepted",
            uri="spotify:track:accepted",
            title="Test Track",
            artist_names=["Test Artist"],
            album="Test Album",
            duration_seconds=180,
            explicit=False,
        )
        score = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )

        # Matched status with candidate should be included
        decision_matched = MatchDecision(
            source_item_id="test123",
            status="matched",
            selected_candidate=candidate,
            score=score,
            reason="Good match",
        )

        result = accepted_uris_in_source_order([track], [decision_matched])
        assert result == ["spotify:track:accepted"]

        # Unmatched status should be excluded (regardless of reason)
        decision_unmatched = MatchDecision(
            source_item_id="test123",
            status="unmatched",
            reason="No suitable match",
        )

        result = accepted_uris_in_source_order([track], [decision_unmatched])
        assert result == []
