"""Cancellation and event emission interfaces for job orchestration.

This module defines the synchronous callback interface for emitting job events
and re-exports the cancellation token protocol for checking cancellation requests.
"""

from typing import Callable, TypeAlias

from playlist_bridge.domain.events import JobEvent

# Type alias for a synchronous event emitter callback
# Accepts any discriminated JobEvent union member and returns None.
# This is a read-only interface: the emitter does not log, serialize,
# or persist events — it only delivers them to the registered handler.
EventEmitter: TypeAlias = Callable[[JobEvent], None]


class FakeCancellationToken:
    """Base fake cancellation token for testing."""

    def __init__(self, cancelled: bool = False) -> None:
        """Initialize the fake token with a cancelled state.

        Args:
            cancelled: Whether the token should be in cancelled state.
        """
        self._cancelled = cancelled

    def is_cancelled(self) -> bool:
        """Return True if the token is in cancelled state."""
        return self._cancelled

    def raise_if_cancelled(self) -> None:
        """Raise CancellationRequested if the token is cancelled."""
        if self._cancelled:
            from playlist_bridge.providers.errors import CancellationRequested
            raise CancellationRequested("test", "cancel_check", "Operation cancelled.")


class ActiveToken(FakeCancellationToken):
    """A cancellation token that is never cancelled (active state).

    This fake always returns False for is_cancelled() and never raises
    CancellationRequested from raise_if_cancelled().
    """

    def __init__(self) -> None:
        """Initialize an active (non-cancelled) token."""
        super().__init__(cancelled=False)


class CancelledToken(FakeCancellationToken):
    """A cancellation token that is already cancelled.

    This fake always returns True for is_cancelled() and always raises
    CancellationRequested from raise_if_cancelled().
    """

    def __init__(self) -> None:
        """Initialize a cancelled token."""
        super().__init__(cancelled=True)


def __getattr__(name: str):
    """Lazy import of CancellationToken from providers.youtube to avoid circular imports."""
    if name == "CancellationToken":
        from playlist_bridge.providers.youtube import CancellationToken
        return CancellationToken
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["EventEmitter", "CancellationToken", "FakeCancellationToken", "ActiveToken", "CancelledToken"]
