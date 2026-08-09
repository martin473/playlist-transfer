"""Integration tests for resume reconciliation and job stages."""

import pytest

from playlist_bridge.domain.models import SourceTrack, MatchDecision
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

        decisions = [
            MatchDecision(
                source_item_id="vid001",
                destination_uri="spotify:track:accepted1",
                destination_track_id="accepted1",
                destination_title="Track 1 - Available",
                destination_artist_names=["Artist One"],
                score=0.95,
                decision_type="accepted",
                confidence=0.9,
            ),
            MatchDecision(
                source_item_id="vid002",
                destination_uri="spotify:track:unavailable",
                destination_track_id="unavailable",
                destination_title="Track 2 - Unavailable",
                destination_artist_names=["Artist Two"],
                score=0.0,
                decision_type="unavailable",
                confidence=0.0,
            ),
            MatchDecision(
                source_item_id="vid003",
                destination_uri="spotify:track:skipped",
                destination_track_id="skipped",
                destination_title="Track 3 - Skipped",
                destination_artist_names=["Artist Three"],
                score=0.0,
                decision_type="skipped",
                confidence=0.0,
            ),
            MatchDecision(
                source_item_id="vid004",
                destination_uri="spotify:track:accepted2",
                destination_track_id="accepted2",
                destination_title="Track 4 - Accepted",
                destination_artist_names=["Artist Four"],
                score=0.98,
                decision_type="accepted",
                confidence=0.95,
            ),
            MatchDecision(
                source_item_id="vid005",
                destination_uri="spotify:track:unmatched",
                destination_track_id="unmatched",
                destination_title="Track 5 - Unmatched",
                destination_artist_names=["Artist Five"],
                score=0.2,
                decision_type="unmatched",
                confidence=0.1,
            ),
            MatchDecision(
                source_item_id="vid006",
                destination_uri="spotify:track:review",
                destination_track_id="review",
                destination_title="Track 6 - Review",
                destination_artist_names=["Artist Six"],
                score=0.6,
                decision_type="review",
                confidence=0.5,
            ),
            MatchDecision(
                source_item_id="vid007",
                destination_uri="spotify:track:accepted3",
                destination_track_id="accepted3",
                destination_title="Track 7 - Accepted Duplicate",
                destination_artist_names=["Artist Four"],
                score=0.92,
                decision_type="accepted",
                confidence=0.85,
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

        decisions = [
            MatchDecision(
                source_item_id="a1",
                destination_uri="spotify:track:accepted_a",
                destination_track_id="accepted_a",
                destination_title="Song A",
                destination_artist_names=["Artist A"],
                score=0.95,
                decision_type="accepted",
                confidence=0.9,
            ),
            # Song B has no decision yet
            MatchDecision(
                source_item_id="c3",
                destination_uri="spotify:track:accepted_c",
                destination_track_id="accepted_c",
                destination_title="Song C",
                destination_artist_names=["Artist C"],
                score=0.85,
                decision_type="accepted",
                confidence=0.8,
            ),
            MatchDecision(
                source_item_id="d4",
                destination_uri="spotify:track:unmatched_d",
                destination_track_id="unmatched_d",
                destination_title="Song D",
                destination_artist_names=["Artist D"],
                score=0.3,
                decision_type="unmatched",
                confidence=0.2,
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

        # Test each decision type
        decision_types = ["accepted", "review", "rejected", "skipped", "unmatched", "unavailable"]

        for decision_type in decision_types:
            decision = MatchDecision(
                source_item_id="test123",
                destination_uri=f"spotify:track:{decision_type}",
                destination_track_id=decision_type,
                destination_title="Test Track",
                destination_artist_names=["Test Artist"],
                score=0.5,
                decision_type=decision_type,
                confidence=0.5,
            )

            result = accepted_uris_in_source_order([track], [decision])

            if decision_type == "accepted":
                assert result == [f"spotify:track:{decision_type}"]
            else:
                assert result == []
