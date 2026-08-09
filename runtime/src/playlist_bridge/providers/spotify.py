"""Spotify provider utilities."""

from typing import Protocol, Sequence, List

from playlist_bridge.domain.models import AccountProfile, SpotifyCandidate, PlaylistReference
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

    def search_tracks(
        self,
        query: str,
        *,
        cancel: CancellationToken,
        limit: int = 10,
    ) -> List[SpotifyCandidate]:
        """Search for tracks on Spotify by query string.

        Args:
            query: Search query string (track title, artist, album, etc.).
            cancel: CancellationToken to check for cancellation requests.
            limit: Maximum number of results to return. Defaults to 10.

        Returns:
            List of SpotifyCandidate objects matching the search query.
            May be empty if no matches are found.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to search.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        ...

    def create_playlist(
        self,
        name: str,
        *,
        cancel: CancellationToken,
        description: str = "",
        public: bool = False,
    ) -> PlaylistReference:
        """Create a new playlist on Spotify.

        Args:
            name: Name of the playlist to create.
            cancel: CancellationToken to check for cancellation requests.
            description: Optional description for the playlist. Defaults to empty.
            public: Whether the playlist should be public. Defaults to False (private).

        Returns:
            PlaylistReference containing the provider, playlist_id, name, and owner.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to create playlists.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        ...

    def add_items(
        self,
        playlist_id: str,
        uris: Sequence[str],
        *,
        cancel: CancellationToken,
        position: int = 0,
    ) -> int:
        """Add items to a Spotify playlist.

        Args:
            playlist_id: ID of the playlist to add items to.
            uris: Sequence of Spotify track URIs to add.
            cancel: CancellationToken to check for cancellation requests.
            position: Position in the playlist to insert items. Defaults to 0 (append).

        Returns:
            Number of items successfully added to the playlist.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to modify the playlist.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        ...

    def replace_items(
        self,
        playlist_id: str,
        uris: Sequence[str],
        *,
        cancel: CancellationToken,
    ) -> int:
        """Replace all items in a Spotify playlist with new items.

        Args:
            playlist_id: ID of the playlist to replace items in.
            uris: Sequence of Spotify track URIs to set as the new playlist contents.
            cancel: CancellationToken to check for cancellation requests.

        Returns:
            Number of items set in the playlist.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to modify the playlist.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        ...

    def read_items(
        self,
        playlist_id: str,
        *,
        cancel: CancellationToken,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SpotifyCandidate]:
        """Read items from a Spotify playlist.

        Args:
            playlist_id: ID of the playlist to read items from.
            cancel: CancellationToken to check for cancellation requests.
            limit: Maximum number of items to return. Defaults to 100.
            offset: Offset for pagination. Defaults to 0.

        Returns:
            List of SpotifyCandidate objects representing the tracks in the playlist.
            May be empty if the playlist has no items or the offset exceeds the total.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to view the playlist.
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
