"""Unit tests for job stages and runner functions."""

import pytest

from playlist_bridge.domain.models import SourceTrack, MatchDecision
from playlist_bridge.jobs.runner import accepted_uris_in_source_order


class TestAcceptedUrisInSourceOrder:
    """Tests for the accepted_uris_in_source_order function."""

    def test_returns_accepted_uris_in_order(self) -> None:
        """Test that accepted URIs are returned in source position order."""
        # Create tracks in source order
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        track2 = SourceTrack(
            position=1,
            title="Song B",
            artist_names=["Artist B"],
            duration_seconds=200,
            video_id="vid2",
            availability="available",
        )
        track3 = SourceTrack(
            position=2,
            title="Song C",
            artist_names=["Artist C"],
            duration_seconds=190,
            video_id="vid3",
            availability="available",
        )

        # Create decisions - only track1 and track3 are accepted
        decision1 = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Song A",
            destination_artist_names=["Artist A"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Song B",
            destination_artist_names=["Artist B"],
            score=0.3,
            decision_type="unmatched",
            confidence=0.2,
        )
        decision3 = MatchDecision(
            source_item_id="vid3",
            destination_uri="spotify:track:uri3",
            destination_track_id="uri3",
            destination_title="Song C",
            destination_artist_names=["Artist C"],
            score=0.85,
            decision_type="accepted",
            confidence=0.8,
        )

        tracks = [track1, track2, track3]
        decisions = [decision1, decision2, decision3]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Should include only accepted URIs in source order
        expected = ["spotify:track:uri1", "spotify:track:uri3"]
        assert result == expected

    def test_skips_unavailable_tracks(self) -> None:
        """Test that unavailable tracks are skipped."""
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="unavailable",
        )
        track2 = SourceTrack(
            position=1,
            title="Song B",
            artist_names=["Artist B"],
            duration_seconds=200,
            video_id="vid2",
            availability="available",
        )

        decision1 = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Song A",
            destination_artist_names=["Artist A"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Song B",
            destination_artist_names=["Artist B"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only track2 should be included (track1 is unavailable)
        expected = ["spotify:track:uri2"]
        assert result == expected

    def test_skips_skipped_tracks(self) -> None:
        """Test that skipped tracks are excluded."""
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        track2 = SourceTrack(
            position=1,
            title="Song B",
            artist_names=["Artist B"],
            duration_seconds=200,
            video_id="vid2",
            availability="available",
        )

        decision1 = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Song A",
            destination_artist_names=["Artist A"],
            score=0.95,
            decision_type="skipped",
            confidence=0.9,
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Song B",
            destination_artist_names=["Artist B"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        expected = ["spotify:track:uri2"]
        assert result == expected

    def test_skips_unmatched_tracks(self) -> None:
        """Test that unmatched tracks are excluded."""
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        track2 = SourceTrack(
            position=1,
            title="Song B",
            artist_names=["Artist B"],
            duration_seconds=200,
            video_id="vid2",
            availability="available",
        )

        decision1 = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Song A",
            destination_artist_names=["Artist A"],
            score=0.3,
            decision_type="unmatched",
            confidence=0.2,
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Song B",
            destination_artist_names=["Artist B"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        expected = ["spotify:track:uri2"]
        assert result == expected

    def test_skips_ambiguous_tracks(self) -> None:
        """Test that ambiguous tracks are excluded."""
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        track2 = SourceTrack(
            position=1,
            title="Song B",
            artist_names=["Artist B"],
            duration_seconds=200,
            video_id="vid2",
            availability="available",
        )

        decision1 = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Song A",
            destination_artist_names=["Artist A"],
            score=0.5,
            decision_type="review",
            confidence=0.4,
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Song B",
            destination_artist_names=["Artist B"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        expected = ["spotify:track:uri2"]
        assert result == expected

    def test_handles_missing_decisions(self) -> None:
        """Test that tracks without decisions are skipped."""
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        track2 = SourceTrack(
            position=1,
            title="Song B",
            artist_names=["Artist B"],
            duration_seconds=200,
            video_id="vid2",
            availability="available",
        )

        decision2 = MatchDecision(
            source_item_id="vid2",
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Song B",
            destination_artist_names=["Artist B"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        tracks = [track1, track2]
        decisions = [decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only track2 has a decision
        expected = ["spotify:track:uri2"]
        assert result == expected

    def test_handles_empty_inputs(self) -> None:
        """Test that empty inputs return empty list."""
        result = accepted_uris_in_source_order([], [])
        assert result == []

    def test_maintains_order_with_duplicates(self) -> None:
        """Test that duplicate source items remain duplicated in output."""
        # Two tracks with the same video_id but different positions
        track1 = SourceTrack(
            position=0,
            title="Song A",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        track2 = SourceTrack(
            position=1,
            title="Song A (repeat)",
            artist_names=["Artist A"],
            duration_seconds=180,
            video_id="vid1",  # Same video_id
            availability="available",
        )

        # Only one decision for this video_id
        decision1 = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Song A",
            destination_artist_names=["Artist A"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        tracks = [track1, track2]
        decisions = [decision1]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Both tracks are included with the same URI (duplicated)
        expected = ["spotify:track:uri1", "spotify:track:uri1"]
        assert result == expected
