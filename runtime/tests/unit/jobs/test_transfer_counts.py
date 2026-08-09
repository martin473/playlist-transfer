"""Unit tests for transfer count calculation."""

import pytest

from playlist_bridge.domain.models import SourceTrack, MatchDecision
from playlist_bridge.jobs.runner import calculate_transfer_counts


class TestCalculateTransferCounts:
    """Tests for the calculate_transfer_counts function."""

    def test_all_tracks_available_and_matched(self) -> None:
        """Test that all available tracks with accepted decisions are counted as matched."""
        tracks = [
            SourceTrack(
                position=0,
                title="Song A",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="vid1",
                availability="available",
            ),
            SourceTrack(
                position=1,
                title="Song B",
                artist_names=["Artist B"],
                duration_seconds=200,
                video_id="vid2",
                availability="available",
            ),
        ]
        decisions = [
            MatchDecision(
                source_item_id="vid1",
                destination_uri="spotify:track:uri1",
                destination_track_id="uri1",
                destination_title="Song A",
                destination_artist_names=["Artist A"],
                score=0.95,
                decision_type="accepted",
                confidence=0.9,
            ),
            MatchDecision(
                source_item_id="vid2",
                destination_uri="spotify:track:uri2",
                destination_track_id="uri2",
                destination_title="Song B",
                destination_artist_names=["Artist B"],
                score=0.9,
                decision_type="accepted",
                confidence=0.85,
            ),
        ]

        counts = calculate_transfer_counts(tracks, decisions)

        assert counts.matched == 2
        assert counts.ambiguous == 0
        assert counts.unmatched == 0
        assert counts.unavailable == 0
        assert counts.skipped == 0
        assert counts.non_track == 0

    def test_mixed_decision_types(self) -> None:
        """Test that different decision types are counted correctly."""
        tracks = [
            SourceTrack(
                position=0,
                title="Track 1",
                artist_names=["Artist 1"],
                duration_seconds=180,
                video_id="vid1",
                availability="available",
            ),
            SourceTrack(
                position=1,
                title="Track 2",
                artist_names=["Artist 2"],
                duration_seconds=190,
                video_id="vid2",
                availability="available",
            ),
            SourceTrack(
                position=2,
                title="Track 3",
                artist_names=["Artist 3"],
                duration_seconds=200,
                video_id="vid3",
                availability="available",
            ),
            SourceTrack(
                position=3,
                title="Track 4",
                artist_names=["Artist 4"],
                duration_seconds=210,
                video_id="vid4",
                availability="available",
            ),
            SourceTrack(
                position=4,
                title="Track 5",
                artist_names=["Artist 5"],
                duration_seconds=220,
                video_id="vid5",
                availability="available",
            ),
            SourceTrack(
                position=5,
                title="Track 6",
                artist_names=["Artist 6"],
                duration_seconds=230,
                video_id="vid6",
                availability="available",
            ),
        ]

        decisions = [
            MatchDecision(
                source_item_id="vid1",
                destination_uri="spotify:track:uri1",
                destination_track_id="uri1",
                destination_title="Track 1",
                destination_artist_names=["Artist 1"],
                score=0.95,
                decision_type="accepted",
                confidence=0.9,
            ),
            MatchDecision(
                source_item_id="vid2",
                destination_uri="spotify:track:uri2",
                destination_track_id="uri2",
                destination_title="Track 2",
                destination_artist_names=["Artist 2"],
                score=0.5,
                decision_type="ambiguous",
                confidence=0.5,
            ),
            MatchDecision(
                source_item_id="vid3",
                destination_uri="spotify:track:uri3",
                destination_track_id="uri3",
                destination_title="Track 3",
                destination_artist_names=["Artist 3"],
                score=0.0,
                decision_type="unmatched",
                confidence=0.0,
            ),
            MatchDecision(
                source_item_id="vid4",
                destination_uri="spotify:track:uri4",
                destination_track_id="uri4",
                destination_title="Track 4",
                destination_artist_names=["Artist 4"],
                score=0.0,
                decision_type="skipped",
                confidence=0.0,
            ),
            MatchDecision(
                source_item_id="vid5",
                destination_uri="spotify:track:uri5",
                destination_track_id="uri5",
                destination_title="Track 5",
                destination_artist_names=["Artist 5"],
                score=0.0,
                decision_type="non_track",
                confidence=0.0,
            ),
            # vid6 has no decision
        ]

        counts = calculate_transfer_counts(tracks, decisions)

        assert counts.matched == 1  # vid1
        assert counts.ambiguous == 1  # vid2
        assert counts.unmatched == 2  # vid3 + vid6 (no decision)
        assert counts.unavailable == 0
        assert counts.skipped == 1  # vid4
        assert counts.non_track == 1  # vid5

    def test_unavailable_tracks_are_counted_separately(self) -> None:
        """Test that unavailable tracks are counted in unavailable count."""
        tracks = [
            SourceTrack(
                position=0,
                title="Available Track",
                artist_names=["Artist A"],
                duration_seconds=180,
                video_id="vid1",
                availability="available",
            ),
            SourceTrack(
                position=1,
                title="Unavailable Track",
                artist_names=["Artist B"],
                duration_seconds=200,
                video_id="vid2",
                availability="unavailable",
            ),
            SourceTrack(
                position=2,
                title="Another Available Track",
                artist_names=["Artist C"],
                duration_seconds=190,
                video_id="vid3",
                availability="available",
            ),
        ]

        decisions = [
            MatchDecision(
                source_item_id="vid1",
                destination_uri="spotify:track:uri1",
                destination_track_id="uri1",
                destination_title="Available Track",
                destination_artist_names=["Artist A"],
                score=0.95,
                decision_type="accepted",
                confidence=0.9,
            ),
            MatchDecision(
                source_item_id="vid2",
                destination_uri="spotify:track:uri2",
                destination_track_id="uri2",
                destination_title="Unavailable Track",
                destination_artist_names=["Artist B"],
                score=0.0,
                decision_type="accepted",  # Even if accepted, it should count as unavailable
                confidence=0.9,
            ),
            MatchDecision(
                source_item_id="vid3",
                destination_uri="spotify:track:uri3",
                destination_track_id="uri3",
                destination_title="Another Available Track",
                destination_artist_names=["Artist C"],
                score=0.9,
                decision_type="accepted",
                confidence=0.85,
            ),
        ]

        counts = calculate_transfer_counts(tracks, decisions)

        # Only available tracks should count toward matched
        assert counts.matched == 2  # vid1 and vid3
        assert counts.unavailable == 1  # vid2
        assert counts.ambiguous == 0
        assert counts.unmatched == 0
        assert counts.skipped == 0
        assert counts.non_track == 0

    def test_sum_equals_total_tracks(self) -> None:
        """Test that counts sum to the total number of source tracks."""
        tracks = [
            SourceTrack(
                position=i,
                title=f"Track {i}",
                artist_names=["Artist"],
                duration_seconds=180,
                video_id=f"vid{i}",
                availability="available" if i % 3 != 0 else "unavailable",
            )
            for i in range(10)
        ]

        decisions = []
        decision_types = ["accepted", "ambiguous", "unmatched", "skipped", "non_track"]
        for i, track in enumerate(tracks):
            if track.availability == "unavailable":
                continue
            decision_type = decision_types[i % len(decision_types)]
            decisions.append(
                MatchDecision(
                    source_item_id=track.video_id,
                    destination_uri=f"spotify:track:uri{i}",
                    destination_track_id=f"uri{i}",
                    destination_title=track.title,
                    destination_artist_names=["Artist"],
                    score=0.5,
                    decision_type=decision_type,
                    confidence=0.5,
                )
            )

        counts = calculate_transfer_counts(tracks, decisions)

        total = (
            counts.matched
            + counts.ambiguous
            + counts.unmatched
            + counts.unavailable
            + counts.skipped
            + counts.non_track
        )
        assert total == len(tracks)

    def test_handles_empty_inputs(self) -> None:
        """Test that empty inputs return zero counts."""
        counts = calculate_transfer_counts([], [])

        assert counts.matched == 0
        assert counts.ambiguous == 0
        assert counts.unmatched == 0
        assert counts.unavailable == 0
        assert counts.skipped == 0
        assert counts.non_track == 0

    def test_review_decision_counted_as_unmatched(self) -> None:
        """Test that review decisions are counted as unmatched."""
        track = SourceTrack(
            position=0,
            title="Review Track",
            artist_names=["Artist"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        decision = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Review Track",
            destination_artist_names=["Artist"],
            score=0.6,
            decision_type="review",
            confidence=0.5,
        )

        counts = calculate_transfer_counts([track], [decision])

        assert counts.matched == 0
        assert counts.ambiguous == 0
        assert counts.unmatched == 1
        assert counts.unavailable == 0
        assert counts.skipped == 0
        assert counts.non_track == 0

    def test_rejected_decision_counted_as_unmatched(self) -> None:
        """Test that rejected decisions are counted as unmatched."""
        track = SourceTrack(
            position=0,
            title="Rejected Track",
            artist_names=["Artist"],
            duration_seconds=180,
            video_id="vid1",
            availability="available",
        )
        decision = MatchDecision(
            source_item_id="vid1",
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Rejected Track",
            destination_artist_names=["Artist"],
            score=0.3,
            decision_type="rejected",
            confidence=0.2,
        )

        counts = calculate_transfer_counts([track], [decision])

        assert counts.matched == 0
        assert counts.ambiguous == 0
        assert counts.unmatched == 1
        assert counts.unavailable == 0
        assert counts.skipped == 0
        assert counts.non_track == 0

    def test_source_item_id_mapping_uses_video_id(self) -> None:
        """Test that the function correctly maps source_item_id to video_id."""
        track = SourceTrack(
            position=0,
            title="Test Track",
            artist_names=["Artist"],
            duration_seconds=180,
            video_id="abc123",
            availability="available",
        )
        decision = MatchDecision(
            source_item_id="abc123",  # Same as video_id
            destination_uri="spotify:track:uri1",
            destination_track_id="uri1",
            destination_title="Test Track",
            destination_artist_names=["Artist"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        counts = calculate_transfer_counts([track], [decision])

        assert counts.matched == 1

        # Mismatched source_item_id should not match
        decision2 = MatchDecision(
            source_item_id="xyz789",  # Different from video_id
            destination_uri="spotify:track:uri2",
            destination_track_id="uri2",
            destination_title="Test Track",
            destination_artist_names=["Artist"],
            score=0.95,
            decision_type="accepted",
            confidence=0.9,
        )

        counts2 = calculate_transfer_counts([track], [decision2])

        assert counts2.matched == 0
        assert counts2.unmatched == 1
