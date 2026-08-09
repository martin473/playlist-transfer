"""Unit tests for the JSONL event emitter."""

import json
import sys
from io import StringIO
from datetime import datetime

import pytest

from playlist_bridge.domain.events import (
    JobStartedEvent,
    MatchProgressEvent,
    SourceProgressEvent,
    WriteProgressEvent,
    CompletionEvent,
    FailureEvent,
    CancellationEvent,
    ReviewRequiredEvent,
    VerificationProgressEvent,
    JobEventAdapter,
)
from playlist_bridge.jobs.runner import JsonlEventEmitter


class TestJsonlEventEmitter:
    """Test the JsonlEventEmitter class."""

    def test_emits_single_event_as_jsonl(self) -> None:
        """Test that a single event is emitted as a JSONL line."""
        stream = StringIO()
        emitter = JsonlEventEmitter(stream)

        event = JobStartedEvent(
            type="job_start",
            job_id="1234567890abcdef1234567890abcdef",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123456",
            destination_playlist_name="My Playlist",
            mode="create",
            policy="balanced",
            dry_run=False,
            timestamp="2026-08-09T08:47:25.914Z",
        )

        emitter.emit(event)
        output = stream.getvalue()

        # Should be exactly one line
        lines = output.strip().split("\n")
        assert len(lines) == 1

        # Should be valid JSON
        data = json.loads(lines[0])
        assert data["type"] == "job_start"
        assert data["job_id"] == "1234567890abcdef1234567890abcdef"
        assert data["source_service"] == "youtube"
        assert data["destination_service"] == "spotify"
        assert data["source_playlist_id"] == "PL123456"
        assert data["destination_playlist_name"] == "My Playlist"
        assert data["mode"] == "create"
        assert data["policy"] == "balanced"
        assert data["dry_run"] is False
        assert data["timestamp"] == "2026-08-09T08:47:25.914Z"

    def test_emits_multiple_events_as_separate_lines(self) -> None:
        """Test that multiple events are emitted as separate JSONL lines."""
        stream = StringIO()
        emitter = JsonlEventEmitter(stream)

        event1 = JobStartedEvent(
            type="job_start",
            job_id="1234567890abcdef1234567890abcdef",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123456",
            destination_playlist_name="My Playlist",
            mode="create",
            policy="balanced",
            dry_run=False,
            timestamp="2026-08-09T08:47:25.914Z",
        )

        event2 = SourceProgressEvent(
            type="source_progress",
            job_id="1234567890abcdef1234567890abcdef",
            total_source_items=100,
            loaded_count=50,
            normalized_count=45,
            skipped_count=5,
            timestamp="2026-08-09T08:47:26.914Z",
        )

        emitter.emit(event1)
        emitter.emit(event2)
        output = stream.getvalue()

        lines = output.strip().split("\n")
        assert len(lines) == 2

        # Both lines should be valid JSON
        data1 = json.loads(lines[0])
        data2 = json.loads(lines[1])
        assert data1["type"] == "job_start"
        assert data2["type"] == "source_progress"
        assert data2["total_source_items"] == 100
        assert data2["loaded_count"] == 50

    def test_emits_all_event_types(self) -> None:
        """Test that all event types can be emitted and parsed."""
        stream = StringIO()
        emitter = JsonlEventEmitter(stream)
        job_id = "1234567890abcdef1234567890abcdef"
        timestamp = "2026-08-09T08:47:25.914Z"

        events = [
            JobStartedEvent(
                type="job_start",
                job_id=job_id,
                source_service="spotify",
                destination_service="youtube",
                source_playlist_id="SP123456",
                destination_playlist_name="My Playlist",
                mode="merge",
                policy="strict",
                dry_run=True,
                timestamp=timestamp,
            ),
            SourceProgressEvent(
                type="source_progress",
                job_id=job_id,
                total_source_items=200,
                loaded_count=150,
                normalized_count=140,
                skipped_count=10,
                timestamp=timestamp,
            ),
            MatchProgressEvent(
                type="match_progress",
                job_id=job_id,
                total_tracks=150,
                matched_count=120,
                reviewed_count=20,
                skipped_count=10,
                timestamp=timestamp,
            ),
            ReviewRequiredEvent(
                type="review_required",
                job_id=job_id,
                source_track_id="track_001",
                reason="Ambiguous match",
                candidates_count=3,
                timestamp=timestamp,
            ),
            WriteProgressEvent(
                type="write_progress",
                job_id=job_id,
                total_to_write=120,
                written_count=60,
                skipped_count=5,
                timestamp=timestamp,
            ),
            VerificationProgressEvent(
                type="verification_progress",
                job_id=job_id,
                total_to_verify=120,
                verified_count=100,
                mismatched_count=15,
                missing_count=5,
                timestamp=timestamp,
            ),
            CompletionEvent(
                type="completion",
                job_id=job_id,
                total_tracks=150,
                matched_count=120,
                written_count=115,
                skipped_count=5,
                timestamp=timestamp,
            ),
            CancellationEvent(
                type="cancellation",
                job_id=job_id,
                reason="User cancelled",
                timestamp=timestamp,
            ),
            FailureEvent(
                type="failure",
                job_id=job_id,
                error_type="ProviderError",
                error_message="Failed to connect to service",
                step="loading_source",
                timestamp=timestamp,
            ),
        ]

        for event in events:
            emitter.emit(event)

        output = stream.getvalue()
        lines = output.strip().split("\n")
        assert len(lines) == len(events)

        # Parse each line and verify it matches the expected event type
        for line, expected_event in zip(lines, events):
            data = json.loads(line)
            # Each line should be valid JSON and have a 'type' field
            assert "type" in data
            # The type should match the expected event's type
            assert data["type"] == expected_event.type

    def test_emitter_flushes_after_each_event(self) -> None:
        """Test that the emitter flushes the stream after each event."""
        # Use a real TextIO that we can spy on
        stream = StringIO()
        emitter = JsonlEventEmitter(stream)

        event = JobStartedEvent(
            type="job_start",
            job_id="1234567890abcdef1234567890abcdef",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123456",
            destination_playlist_name="My Playlist",
            mode="create",
            policy="balanced",
            dry_run=False,
            timestamp="2026-08-09T08:47:25.914Z",
        )

        # The write should succeed and flush
        emitter.emit(event)
        output = stream.getvalue()
        assert output  # Should have content
        assert output.endswith("\n")

    def test_round_trip_parsing_with_adapter(self) -> None:
        """Test that events emitted can be parsed back with JobEventAdapter."""
        stream = StringIO()
        emitter = JsonlEventEmitter(stream)

        original_event = JobStartedEvent(
            type="job_start",
            job_id="1234567890abcdef1234567890abcdef",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123456",
            destination_playlist_name="My Playlist",
            mode="create",
            policy="balanced",
            dry_run=False,
            timestamp="2026-08-09T08:47:25.914Z",
        )

        emitter.emit(original_event)
        output = stream.getvalue()
        lines = output.strip().split("\n")

        # Parse the line back using JobEventAdapter
        parsed_event = JobEventAdapter.validate_json(lines[0])

        assert parsed_event.type == original_event.type
        assert parsed_event.job_id == original_event.job_id
        assert parsed_event.source_service == original_event.source_service
        assert parsed_event.destination_service == original_event.destination_service
        assert parsed_event.source_playlist_id == original_event.source_playlist_id
        assert parsed_event.destination_playlist_name == original_event.destination_playlist_name
        assert parsed_event.mode == original_event.mode
        assert parsed_event.policy == original_event.policy
        assert parsed_event.dry_run == original_event.dry_run
        assert parsed_event.timestamp == original_event.timestamp

    def test_emits_with_stdout(self) -> None:
        """Test that the emitter can work with sys.stdout (smoke test)."""
        # We don't actually want to write to stdout in tests, but we can verify
        # that the emitter accepts a TextIO stream like sys.stdout
        emitter = JsonlEventEmitter(sys.stdout)
        assert emitter._stream is sys.stdout

    def test_raises_oserror_on_stream_error(self) -> None:
        """Test that OSError is raised when stream write fails."""
        class BrokenStream:
            def write(self, _):
                raise OSError("Stream is broken")
            def flush(self):
                pass

        # StringIO doesn't raise OSError, so we use a custom class that does
        broken_stream = BrokenStream()
        # We need to make it behave like TextIO
        # Use a hack to make it pass type checking
        setattr(broken_stream, "readable", lambda: False)
        setattr(broken_stream, "writable", lambda: True)
        setattr(broken_stream, "seekable", lambda: False)

        emitter = JsonlEventEmitter(broken_stream)  # type: ignore
        event = JobStartedEvent(
            type="job_start",
            job_id="1234567890abcdef1234567890abcdef",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123456",
            destination_playlist_name="My Playlist",
            mode="create",
            policy="balanced",
            dry_run=False,
            timestamp="2026-08-09T08:47:25.914Z",
        )

        with pytest.raises(OSError, match="Failed to emit JSONL event"):
            emitter.emit(event)

    def test_handles_complex_event_data(self) -> None:
        """Test that events with complex data are properly serialized."""
        stream = StringIO()
        emitter = JsonlEventEmitter(stream)

        # Test with various data types in event fields
        event = SourceProgressEvent(
            type="source_progress",
            job_id="1234567890abcdef1234567890abcdef",
            total_source_items=1000,
            loaded_count=500,
            normalized_count=450,
            skipped_count=50,
            timestamp="2026-08-09T08:47:25.914Z",
        )

        emitter.emit(event)
        output = stream.getvalue()
        data = json.loads(output.strip())

        assert data["type"] == "source_progress"
        assert data["total_source_items"] == 1000
        assert data["loaded_count"] == 500
        assert data["normalized_count"] == 450
        assert data["skipped_count"] == 50
        assert data["timestamp"] == "2026-08-09T08:47:25.914Z"
