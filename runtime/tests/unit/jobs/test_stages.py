"""Unit tests for job stages and runner functions."""

import pytest

from playlist_bridge.domain.models import (
    SourceTrack,
    MatchDecision,
    MatchScore,
    SpotifyCandidate,
)
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

        # Create candidates
        candidate1 = SpotifyCandidate(
            track_id="uri1",
            uri="spotify:track:uri1",
            title="Song A",
            artist_names=["Artist A"],
            album="Album A",
            duration_seconds=180,
            explicit=False,
        )
        candidate3 = SpotifyCandidate(
            track_id="uri3",
            uri="spotify:track:uri3",
            title="Song C",
            artist_names=["Artist C"],
            album="Album C",
            duration_seconds=190,
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
        score3 = MatchScore(
            title_similarity=0.85,
            artist_similarity=0.8,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.85,
            reasons=["Good match"],
        )

        # Create decisions - only track1 and track3 are accepted
        decision1 = MatchDecision(
            source_item_id="vid1",
            status="matched",
            selected_candidate=candidate1,
            score=score1,
            reason="Good match",
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            status="unmatched",
            reason="No suitable match",
        )
        decision3 = MatchDecision(
            source_item_id="vid3",
            status="matched",
            selected_candidate=candidate3,
            score=score3,
            reason="Good match",
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

        candidate1 = SpotifyCandidate(
            track_id="uri1",
            uri="spotify:track:uri1",
            title="Song A",
            artist_names=["Artist A"],
            album="Album A",
            duration_seconds=180,
            explicit=False,
        )
        candidate2 = SpotifyCandidate(
            track_id="uri2",
            uri="spotify:track:uri2",
            title="Song B",
            artist_names=["Artist B"],
            album="Album B",
            duration_seconds=200,
            explicit=False,
        )

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
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )

        decision1 = MatchDecision(
            source_item_id="vid1",
            status="matched",
            selected_candidate=candidate1,
            score=score1,
            reason="Good match",
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            status="matched",
            selected_candidate=candidate2,
            score=score2,
            reason="Good match",
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

        # Track1 is skipped (not matched)
        decision1 = MatchDecision(
            source_item_id="vid1",
            status="unmatched",
            reason="Skipped by user",
        )

        candidate2 = SpotifyCandidate(
            track_id="uri2",
            uri="spotify:track:uri2",
            title="Song B",
            artist_names=["Artist B"],
            album="Album B",
            duration_seconds=200,
            explicit=False,
        )
        score2 = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            status="matched",
            selected_candidate=candidate2,
            score=score2,
            reason="Good match",
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only track2 should be included
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

        # Track1 is unmatched
        decision1 = MatchDecision(
            source_item_id="vid1",
            status="unmatched",
            reason="No suitable match found",
        )

        candidate2 = SpotifyCandidate(
            track_id="uri2",
            uri="spotify:track:uri2",
            title="Song B",
            artist_names=["Artist B"],
            album="Album B",
            duration_seconds=200,
            explicit=False,
        )
        score2 = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            status="matched",
            selected_candidate=candidate2,
            score=score2,
            reason="Good match",
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only track2 should be included
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

        # Track1 is ambiguous (unmatched with no selected candidate)
        decision1 = MatchDecision(
            source_item_id="vid1",
            status="unmatched",
            reason="Ambiguous match",
        )

        candidate2 = SpotifyCandidate(
            track_id="uri2",
            uri="spotify:track:uri2",
            title="Song B",
            artist_names=["Artist B"],
            album="Album B",
            duration_seconds=200,
            explicit=False,
        )
        score2 = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            status="matched",
            selected_candidate=candidate2,
            score=score2,
            reason="Good match",
        )

        tracks = [track1, track2]
        decisions = [decision1, decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only track2 should be included
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

        # Only decision for track2
        candidate2 = SpotifyCandidate(
            track_id="uri2",
            uri="spotify:track:uri2",
            title="Song B",
            artist_names=["Artist B"],
            album="Album B",
            duration_seconds=200,
            explicit=False,
        )
        score2 = MatchScore(
            title_similarity=0.95,
            artist_similarity=0.9,
            duration_similarity=1.0,
            version_agreement=1.0,
            unwanted_version_penalty=0.0,
            explicit_state=1.0,
            total_score=0.95,
            reasons=["Good match"],
        )
        decision2 = MatchDecision(
            source_item_id="vid2",
            status="matched",
            selected_candidate=candidate2,
            score=score2,
            reason="Good match",
        )

        tracks = [track1, track2]
        decisions = [decision2]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Only track2 should be included
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
        candidate1 = SpotifyCandidate(
            track_id="uri1",
            uri="spotify:track:uri1",
            title="Song A",
            artist_names=["Artist A"],
            album="Album A",
            duration_seconds=180,
            explicit=False,
        )
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
        decision1 = MatchDecision(
            source_item_id="vid1",
            status="matched",
            selected_candidate=candidate1,
            score=score1,
            reason="Good match",
        )

        tracks = [track1, track2]
        decisions = [decision1]

        result = accepted_uris_in_source_order(tracks, decisions)

        # Both tracks are included with the same URI (duplicated)
        expected = ["spotify:track:uri1", "spotify:track:uri1"]
        assert result == expected
