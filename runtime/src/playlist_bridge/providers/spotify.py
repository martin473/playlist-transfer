"""Spotify provider utilities."""

from typing import Protocol, Sequence

from playlist_bridge.domain.models import AccountProfile
from playlist_bridge.providers.errors import (
    AuthenticationRequired,
    PermissionDenied,
    ProviderNotFound,
    RateLimited,
    InvalidProviderResponse,
    TemporaryProviderFailure,
    CancellationRequested,
)
from playlist_bridge.jobs.cancellation import CancellationToken


class SpotifyAdapter(Protocol):
    """Protocol for interacting with the Spotify API.

    This protocol defines the interface that any Spotify adapter must implement
    to perform operations such as retrieving user identity, searching tracks,
    creating playlists, and managing playlist items.
    """

    def identity(
        self,
        *,
        cancel: CancellationToken,
    ) -> AccountProfile:
        """Retrieve the authenticated user's identity.

        Args:
            cancel: CancellationToken to check for cancellation requests.

        Returns:
            AccountProfile containing the user's provider, account_id,
            display_name, and optional email/username/profile_url.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to view their profile.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        ...


def chunk_uris(uris: Sequence[str], batch_size: int = 100) -> list[tuple[str, ...]]:
    """Split an ordered URI sequence into batches no larger than batch_size.

    Args:
        uris: Sequence of Spotify URIs to chunk.
        batch_size: Maximum number of URIs per batch. Defaults to 100.

    Returns:
        List of tuples, each containing up to batch_size URIs in order.

    Raises:
        ValueError: If batch_size is less than 1.
    """
    if batch_size < 1:
        raise ValueError("batch_size must be at least 1")

    # Ensure we always return tuples for immutability
    return [tuple(uris[i : i + batch_size]) for i in range(0, len(uris), batch_size)]
