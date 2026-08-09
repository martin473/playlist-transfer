"""Unit tests for JSONL event models and discriminated union."""

import pytest
from pydantic import ValidationError
from playlist_bridge.domain.events import (
    JobStartedEvent,
    SourceProgressEvent,
    MatchProgressEvent,
    ReviewRequiredEvent,
    WriteProgressEvent,
    VerificationProgressEvent,
    FailureEvent,
    CancellationEvent,
    CompletionEvent,
    JobEventAdapter,
)


class TestEventModels:
    """Test suite for individual event model validation and serialization."""

    def test_job_started_event(self):
        """Test that JobStartedEvent validates correctly."""
        event = JobStartedEvent(
            type="job_start",
            job_id="job-123",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123",
            destination_playlist_name="My Playlist",
            mode="create",
            policy="balanced",
            dry_run=False,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "job_start"
        assert event.job_id == "job-123"

    def test_source_progress_event(self):
        """Test that SourceProgressEvent validates correctly."""
        event = SourceProgressEvent(
            type="source_progress",
            job_id="job-123",
            total_source_items=100,
            loaded_count=50,
            normalized_count=45,
            skipped_count=5,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "source_progress"
        assert event.loaded_count == 50

    def test_match_progress_event(self):
        """Test that MatchProgressEvent validates correctly."""
        event = MatchProgressEvent(
            type="match_progress",
            job_id="job-123",
            total_tracks=80,
            matched_count=40,
            reviewed_count=10,
            skipped_count=5,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "match_progress"
        assert event.matched_count == 40

    def test_review_required_event(self):
        """Test that ReviewRequiredEvent validates correctly."""
        event = ReviewRequiredEvent(
            type="review_required",
            job_id="job-123",
            source_track_id="track-456",
            reason="Ambiguous match - multiple candidates with similar scores",
            candidates_count=3,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "review_required"
        assert event.source_track_id == "track-456"
        assert event.candidates_count == 3

    def test_write_progress_event(self):
        """Test that WriteProgressEvent validates correctly."""
        event = WriteProgressEvent(
            type="write_progress",
            job_id="job-123",
            total_to_write=60,
            written_count=30,
            skipped_count=2,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "write_progress"
        assert event.written_count == 30

    def test_verification_progress_event(self):
        """Test that VerificationProgressEvent validates correctly."""
        event = VerificationProgressEvent(
            type="verification_progress",
            job_id="job-123",
            total_to_verify=58,
            verified_count=40,
            mismatched_count=3,
            missing_count=2,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "verification_progress"
        assert event.verified_count == 40

    def test_failure_event(self):
        """Test that FailureEvent validates correctly."""
        event = FailureEvent(
            type="failure",
            job_id="job-123",
            error_type="ConnectionError",
            error_message="Failed to connect to Spotify API",
            step="matching",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "failure"
        assert event.error_type == "ConnectionError"

    def test_cancellation_event(self):
        """Test that CancellationEvent validates correctly."""
        event = CancellationEvent(
            type="cancellation",
            job_id="job-123",
            reason="User requested cancellation",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "cancellation"
        assert event.reason == "User requested cancellation"

    def test_completion_event(self):
        """Test that CompletionEvent validates correctly."""
        event = CompletionEvent(
            type="completion",
            job_id="job-123",
            total_tracks=60,
            matched_count=55,
            written_count=50,
            skipped_count=5,
            timestamp="2026-01-01T00:00:00Z",
        )
        assert event.type == "completion"
        assert event.written_count == 50


class TestJobEventUnion:
    """Test suite for the JobEvent discriminated union."""

    @pytest.mark.parametrize(
        "event_type,event_data",
        [
            (
                "job_start",
                {
                    "type": "job_start",
                    "job_id": "job-123",
                    "source_service": "youtube",
                    "destination_service": "spotify",
                    "source_playlist_id": "PL123",
                    "destination_playlist_name": "My Playlist",
                    "mode": "create",
                    "policy": "balanced",
                    "dry_run": False,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "source_progress",
                {
                    "type": "source_progress",
                    "job_id": "job-123",
                    "total_source_items": 100,
                    "loaded_count": 50,
                    "normalized_count": 45,
                    "skipped_count": 5,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "match_progress",
                {
                    "type": "match_progress",
                    "job_id": "job-123",
                    "total_tracks": 80,
                    "matched_count": 40,
                    "reviewed_count": 10,
                    "skipped_count": 5,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "review_required",
                {
                    "type": "review_required",
                    "job_id": "job-123",
                    "source_track_id": "track-456",
                    "reason": "Ambiguous match",
                    "candidates_count": 3,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "write_progress",
                {
                    "type": "write_progress",
                    "job_id": "job-123",
                    "total_to_write": 60,
                    "written_count": 30,
                    "skipped_count": 2,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "verification_progress",
                {
                    "type": "verification_progress",
                    "job_id": "job-123",
                    "total_to_verify": 58,
                    "verified_count": 40,
                    "mismatched_count": 3,
                    "missing_count": 2,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "failure",
                {
                    "type": "failure",
                    "job_id": "job-123",
                    "error_type": "ConnectionError",
                    "error_message": "Failed to connect",
                    "step": "matching",
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "cancellation",
                {
                    "type": "cancellation",
                    "job_id": "job-123",
                    "reason": "User cancelled",
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
            (
                "completion",
                {
                    "type": "completion",
                    "job_id": "job-123",
                    "total_tracks": 60,
                    "matched_count": 55,
                    "written_count": 50,
                    "skipped_count": 5,
                    "timestamp": "2026-01-01T00:00:00Z",
                },
            ),
        ],
    )
    def test_parser_selects_correct_model_by_type(self, event_type, event_data):
        """Test that the JobEvent union parser selects the correct model for each event type."""
        # Parse the event data through the union adapter
        parsed = JobEventAdapter.validate_python(event_data)

        # Verify the parsed object has the correct type
        assert parsed.type == event_type

        # Verify it's an instance of the expected class
        expected_classes = {
            "job_start": JobStartedEvent,
            "source_progress": SourceProgressEvent,
            "match_progress": MatchProgressEvent,
            "review_required": ReviewRequiredEvent,
            "write_progress": WriteProgressEvent,
            "verification_progress": VerificationProgressEvent,
            "failure": FailureEvent,
            "cancellation": CancellationEvent,
            "completion": CompletionEvent,
        }
        assert isinstance(parsed, expected_classes[event_type])

    def test_job_event_union_rejects_unknown_type(self):
        """Test that the JobEvent union rejects unknown event types."""
        invalid_data = {
            "type": "unknown_event",
            "job_id": "job-123",
            "timestamp": "2026-01-01T00:00:00Z",
        }
        with pytest.raises(ValidationError):
            JobEventAdapter.validate_python(invalid_data)

    def test_job_event_union_rejects_missing_required_field(self):
        """Test that the JobEvent union rejects events missing required fields."""
        invalid_data = {
            "type": "job_start",
            "job_id": "job-123",
            # Missing required fields
        }
        with pytest.raises(ValidationError):
            JobEventAdapter.validate_python(invalid_data)
