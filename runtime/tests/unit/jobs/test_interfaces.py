"""Unit tests for job orchestration interfaces: EventEmitter and CancellationToken.

This test module verifies:
1. EventEmitter type alias accepts only JobEvent union members
2. RecordingEventEmitter fake captures events in call order
3. Static typing rejects non-event objects (via type checking, not runtime)
"""

import pytest
from typing import List

from playlist_bridge.domain.events import (
    JobEvent,
    JobStartedEvent,
    SourceProgressEvent,
    MatchProgressEvent,
    ReviewRequiredEvent,
    WriteProgressEvent,
    VerificationProgressEvent,
    FailureEvent,
    CancellationEvent,
    CompletionEvent,
)
from playlist_bridge.jobs.cancellation import EventEmitter, CancellationToken
from playlist_bridge.providers.youtube import CancellationToken as YouTubeCancellationToken


class RecordingEventEmitter:
    """Fake event emitter that records validated events in call order.

    This fake is used for testing to verify that events are emitted in the
    correct sequence without serializing or logging to disk.

    Attributes:
        events: List of events recorded in emission order.
    """

    def __init__(self) -> None:
        """Initialize an empty event recording list."""
        self.events: List[JobEvent] = []

    def emit(self, event: JobEvent) -> None:
        """Record a validated event in call order.

        Args:
            event: A validated JobEvent union member to record.

        Raises:
            TypeError: If the event is not a JobEvent union member.
        """
        # Type guard: ensure the event is a JobEvent union member
        # This is a runtime check to match the static typing contract.
        if not isinstance(event, (
            JobStartedEvent,
            SourceProgressEvent,
            MatchProgressEvent,
            ReviewRequiredEvent,
            WriteProgressEvent,
            VerificationProgressEvent,
            FailureEvent,
            CancellationEvent,
            CompletionEvent,
        )):
            raise TypeError(f"Expected JobEvent, got {type(event).__name__}")
        self.events.append(event)


class TestEventEmitter:
    """Test suite for EventEmitter type alias and recording emitter."""

    def test_event_emitter_type_alias_accepts_job_event(self) -> None:
        """Test that EventEmitter type alias accepts a JobEvent callback."""
        # A simple emitter function that records events
        recorded: List[JobEvent] = []

        def emitter(event: JobEvent) -> None:
            recorded.append(event)

        # Type check: emitter should be assignable to EventEmitter
        # This is a static check, but we verify by calling it with a JobEvent
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
            timestamp="2026-08-09T06:52:13.620Z",
        )

        # The function should be callable with JobEvent
        emitter(event)
        assert len(recorded) == 1
        assert recorded[0] == event

    def test_recording_emitter_stores_events_in_order(self) -> None:
        """Test that RecordingEventEmitter captures events in call order."""
        emitter = RecordingEventEmitter()

        event1 = JobStartedEvent(
            type="job_start",
            job_id="abc123",
            source_service="youtube",
            destination_service="spotify",
            source_playlist_id="PL123",
            destination_playlist_name="Test",
            mode="create",
            policy="strict",
            dry_run=False,
            timestamp="2026-08-09T06:52:13.620Z",
        )
        event2 = SourceProgressEvent(
            type="source_progress",
            job_id="abc123",
            total_source_items=10,
            loaded_count=5,
            normalized_count=4,
            skipped_count=1,
            timestamp="2026-08-09T06:52:14.620Z",
        )

        emitter.emit(event1)
        emitter.emit(event2)

        assert len(emitter.events) == 2
        assert emitter.events[0] == event1
        assert emitter.events[1] == event2

    def test_recording_emitter_rejects_non_job_event(self) -> None:
        """Test that RecordingEventEmitter rejects non-JobEvent objects."""
        emitter = RecordingEventEmitter()

        # Create a non-event object that shouldn't be accepted
        class NotAnEvent:
            pass

        non_event = NotAnEvent()

        with pytest.raises(TypeError, match="Expected JobEvent"):
            emitter.emit(non_event)  # type: ignore

    def test_recording_emitter_handles_all_event_types(self) -> None:
        """Test that RecordingEventEmitter can handle all JobEvent variants."""
        emitter = RecordingEventEmitter()

        # Create one of each event type
        events: List[JobEvent] = [
            JobStartedEvent(
                type="job_start",
                job_id="test123",
                source_service="spotify",
                destination_service="youtube",
                source_playlist_id="spotify:playlist:123",
                destination_playlist_name="Test Playlist",
                mode="merge",
                policy="loose",
                dry_run=True,
                timestamp="2026-08-09T06:52:13.620Z",
            ),
            SourceProgressEvent(
                type="source_progress",
                job_id="test123",
                total_source_items=10,
                loaded_count=10,
                normalized_count=9,
                skipped_count=1,
                timestamp="2026-08-09T06:52:14.620Z",
            ),
            MatchProgressEvent(
                type="match_progress",
                job_id="test123",
                total_tracks=9,
                matched_count=7,
                reviewed_count=2,
                skipped_count=0,
                timestamp="2026-08-09T06:52:15.620Z",
            ),
            ReviewRequiredEvent(
                type="review_required",
                job_id="test123",
                source_track_id="track_001",
                reason="Ambiguous match",
                candidates_count=3,
                timestamp="2026-08-09T06:52:16.620Z",
            ),
            WriteProgressEvent(
                type="write_progress",
                job_id="test123",
                total_to_write=7,
                written_count=5,
                skipped_count=2,
                timestamp="2026-08-09T06:52:17.620Z",
            ),
            VerificationProgressEvent(
                type="verification_progress",
                job_id="test123",
                total_to_verify=5,
                verified_count=3,
                mismatched_count=0,
                missing_count=0,
                timestamp="2026-08-09T06:52:18.620Z",
            ),
            FailureEvent(
                type="failure",
                job_id="test123",
                error_type="AUTH_FAILED",
                error_message="Failed to authenticate",
                step=None,
                timestamp="2026-08-09T06:52:19.620Z",
            ),
            CancellationEvent(
                type="cancellation",
                job_id="test123",
                reason="User requested cancellation",
                timestamp="2026-08-09T06:52:20.620Z",
            ),
            CompletionEvent(
                type="completion",
                job_id="test123",
                total_tracks=7,
                matched_count=5,
                written_count=5,
                skipped_count=2,
                timestamp="2026-08-09T06:52:21.620Z",
            ),
        ]

        # Emit all events
        for event in events:
            emitter.emit(event)

        # Verify all events were recorded in order
        assert len(emitter.events) == len(events)
        for i, event in enumerate(events):
            assert emitter.events[i] == event


class TestCancellationToken:
    """Test suite for CancellationToken protocol compatibility."""

    def test_cancellation_token_re_export(self) -> None:
        """Test that CancellationToken is re-exported from cancellation module."""
        # Import from the cancellation module
        from playlist_bridge.jobs.cancellation import CancellationToken as CT

        # Verify it's the same as the YouTube version
        assert CT is YouTubeCancellationToken

    def test_cancellation_token_protocol_works(self) -> None:
        """Test that CancellationToken protocol can be used with a simple implementation."""
        from playlist_bridge.jobs.cancellation import CancellationToken

        class SimpleToken:
            """Simple cancellation token implementation for testing."""

            def __init__(self, cancelled: bool = False) -> None:
                self._cancelled = cancelled

            def is_cancelled(self) -> bool:
                return self._cancelled

            def raise_if_cancelled(self) -> None:
                if self._cancelled:
                    from playlist_bridge.providers.errors import CancellationRequested
                    raise CancellationRequested("test", "test_op", "Operation cancelled.")

        token: CancellationToken = SimpleToken()
        assert not token.is_cancelled()
        # Active token should not raise
        token.raise_if_cancelled()  # Should not raise

        token = SimpleToken(cancelled=True)
        assert token.is_cancelled()
        # Cancelled token should raise
        with pytest.raises(Exception):  # CancellationRequested
            token.raise_if_cancelled()

    def test_event_emitter_accepts_recording_emitter(self) -> None:
        """Test that RecordingEventEmitter.emit is compatible with EventEmitter type."""
        emitter = RecordingEventEmitter()

        # RecordingEventEmitter.emit should be assignable to EventEmitter
        # We verify by using it as an EventEmitter
        def use_emitter(emitter_func: EventEmitter) -> None:
            event = JobStartedEvent(
                type="job_start",
                job_id="test123",
                source_service="youtube",
                destination_service="spotify",
                source_playlist_id="PL123",
                destination_playlist_name="Test",
                mode="create",
                policy="strict",
                dry_run=False,
                timestamp="2026-08-09T06:52:13.620Z",
            )
            emitter_func(event)

        # Pass the emit method as an EventEmitter
        use_emitter(emitter.emit)

        # Verify the event was recorded
        assert len(emitter.events) == 1
        assert emitter.events[0].job_id == "test123"


class TestCancellationFakes:
    """Test suite for cancellation token fakes: ActiveToken and CancelledToken."""

    def test_active_token_not_cancelled(self) -> None:
        """Test that ActiveToken returns False for is_cancelled and doesn't raise."""
        from playlist_bridge.jobs.cancellation import ActiveToken, CancellationToken

        token: CancellationToken = ActiveToken()
        assert not token.is_cancelled()
        # Should not raise
        token.raise_if_cancelled()

    def test_cancelled_token_is_cancelled(self) -> None:
        """Test that CancelledToken returns True for is_cancelled and raises."""
        from playlist_bridge.jobs.cancellation import CancelledToken, CancellationToken
        from playlist_bridge.providers.errors import CancellationRequested

        token: CancellationToken = CancelledToken()
        assert token.is_cancelled()
        with pytest.raises(CancellationRequested):
            token.raise_if_cancelled()

    def test_fake_cancellation_token_base(self) -> None:
        """Test that FakeCancellationToken can be instantiated with custom state."""
        from playlist_bridge.jobs.cancellation import FakeCancellationToken
        from playlist_bridge.providers.errors import CancellationRequested

        # Active state
        token = FakeCancellationToken(cancelled=False)
        assert not token.is_cancelled()
        token.raise_if_cancelled()  # Should not raise

        # Cancelled state
        token = FakeCancellationToken(cancelled=True)
        assert token.is_cancelled()
        with pytest.raises(CancellationRequested):
            token.raise_if_cancelled()

    def test_active_token_static_type_check(self) -> None:
        """Test that ActiveToken satisfies the CancellationToken protocol."""
        from playlist_bridge.jobs.cancellation import ActiveToken, CancellationToken

        def use_token(token: CancellationToken) -> None:
            assert not token.is_cancelled()
            token.raise_if_cancelled()

        use_token(ActiveToken())

    def test_cancelled_token_static_type_check(self) -> None:
        """Test that CancelledToken satisfies the CancellationToken protocol."""
        from playlist_bridge.jobs.cancellation import CancelledToken, CancellationToken
        from playlist_bridge.providers.errors import CancellationRequested

        def use_token(token: CancellationToken) -> None:
            assert token.is_cancelled()
            with pytest.raises(CancellationRequested):
                token.raise_if_cancelled()

        use_token(CancelledToken())
