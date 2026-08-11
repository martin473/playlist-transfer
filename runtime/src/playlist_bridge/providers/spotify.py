"""Spotify provider utilities."""

from typing import Protocol, Sequence, List

from playlist_bridge.domain.models import AccountProfile, SpotifyCandidate, PlaylistReference
from spotipy.exceptions import SpotifyException

from playlist_bridge.providers.errors import (
    AuthenticationRequired,
    PermissionDenied,
    ProviderNotFound,
    RateLimited,
    InvalidProviderResponse,
    TemporaryProviderFailure,
    CancellationRequested,
    ProviderError,
)
from playlist_bridge.jobs.cancellation import CancellationToken


def map_spotify_error(error: SpotifyException, operation: str) -> ProviderError:
    """Map Spotify API exceptions to provider errors.

    Args:
        error: The SpotifyException raised by the Spotify API.
        operation: The operation that was being performed.

    Returns:
        A ProviderError subclass appropriate for the exception type.

    The mapping follows this scheme:
        - 401/403: AuthenticationRequired or PermissionDenied
        - 404: ProviderNotFound
        - 429: RateLimited
        - 5xx: TemporaryProviderFailure
        - Other/unknown: InvalidProviderResponse or ProviderError
    """
    service = "spotify"

    # Handle cases where error.http_status is available
    http_status = getattr(error, "http_status", None)
    if http_status is not None:
        if http_status == 401:
            return AuthenticationRequired(
                service,
                operation,
                f"Spotify authentication required for {operation}. Please check your credentials."
            )
        elif http_status == 403:
            return PermissionDenied(
                service,
                operation,
                f"Spotify permission denied for {operation}. You may lack the required scope."
            )
        elif http_status == 404:
            return ProviderNotFound(
                service,
                operation,
                f"Spotify resource not found for {operation}. The requested item may not exist."
            )
        elif http_status == 429:
            # Attempt to extract retry-after header
            retry_after = None
            if hasattr(error, "headers"):
                retry_after = error.headers.get("Retry-After")
            elif hasattr(error, "response") and hasattr(error.response, "headers"):
                retry_after = error.response.headers.get("Retry-After")
            elif hasattr(error, "resp") and hasattr(error.resp, "headers"):
                retry_after = error.resp.headers.get("Retry-After")
            
            message = f"Spotify rate limit exceeded for {operation}. Please wait before retrying."
            if retry_after:
                message = f"Spotify rate limit exceeded for {operation}. Retry-After: {retry_after} seconds."
            
            return RateLimited(service, operation, message)
        elif 500 <= http_status < 600:
            return TemporaryProviderFailure(
                service,
                operation,
                f"Spotify server error ({http_status}) for {operation}. Please try again later."
            )

    # If no http_status or unknown status code, use error message to infer
    error_msg = str(error).lower()
    if "authentication" in error_msg or "authorization" in error_msg or "token" in error_msg:
        return AuthenticationRequired(
            service,
            operation,
            f"Spotify authentication required for {operation}. Please check your credentials."
        )
    elif "permission" in error_msg or "scope" in error_msg or "forbidden" in error_msg:
        return PermissionDenied(
            service,
            operation,
            f"Spotify permission denied for {operation}. You may lack the required scope."
        )
    elif "not found" in error_msg or "does not exist" in error_msg:
        return ProviderNotFound(
            service,
            operation,
            f"Spotify resource not found for {operation}. The requested item may not exist."
        )
    elif "rate limit" in error_msg or "too many requests" in error_msg:
        # Attempt to extract retry-after header from the exception if available
        retry_after = None
        if hasattr(error, "headers"):
            retry_after = error.headers.get("Retry-After")
        elif hasattr(error, "response") and hasattr(error.response, "headers"):
            retry_after = error.response.headers.get("Retry-After")
        elif hasattr(error, "resp") and hasattr(error.resp, "headers"):
            retry_after = error.resp.headers.get("Retry-After")
        
        message = f"Spotify rate limit exceeded for {operation}. Please wait before retrying."
        if retry_after:
            message = f"Spotify rate limit exceeded for {operation}. Retry-After: {retry_after} seconds."
        
        return RateLimited(service, operation, message)
    elif "server" in error_msg or "internal" in error_msg or "temporary" in error_msg:
        return TemporaryProviderFailure(
            service,
            operation,
            f"Spotify temporary failure for {operation}. Please try again later."
        )
    else:
        return InvalidProviderResponse(
            service,
            operation,
            f"Spotify returned an unexpected response for {operation}: {str(error)}"
        )


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

    def user_playlists(
        self,
        *,
        cancel: CancellationToken,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PlaylistReference]:
        """List the authenticated user's playlists.

        Args:
            cancel: CancellationToken to check for cancellation requests.
            limit: Maximum number of playlists to return. Defaults to 50.
            offset: Offset for pagination. Defaults to 0.

        Returns:
            List of PlaylistReference objects representing the user's playlists.
            May be empty if the user has no playlists or the offset exceeds the total.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to view their playlists.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        ...


class AuthenticatedSpotifyAdapter:
    """Adapter wrapping an authenticated Spotipy client.

    This adapter implements the SpotifyAdapter protocol by delegating
    to an authenticated Spotipy client instance. Construction of the
    adapter does not perform any network requests.

    Args:
        client: An authenticated Spotipy client instance.
    """

    def __init__(self, client: spotipy.Spotify) -> None:
        """Initialize the adapter with an authenticated Spotipy client.

        Args:
            client: An authenticated Spotipy client instance.
        """
        self._client = client

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
        cancel.raise_if_cancelled()
        try:
            user_info = self._client.me()
            if user_info is None:
                raise InvalidProviderResponse(
                    "spotify",
                    "identity",
                    "Spotify returned null response for user identity"
                )
            # Extract account_id from the user info
            account_id = user_info.get("id", "")
            display_name = user_info.get("display_name", "")
            return AccountProfile(
                profile_name="",
                service="spotify",
                provider_user_id=account_id,
                display_name=display_name,
            )
        except SpotifyException as e:
            raise map_spotify_error(e, "identity")

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
        cancel.raise_if_cancelled()
        try:
            results = self._client.search(q=query, type="track", limit=limit)
            if results is None:
                return []
            tracks = results.get("tracks", {})
            items = tracks.get("items", [])
            candidates: List[SpotifyCandidate] = []
            for item in items:
                if item is None:
                    continue
                track_id = item.get("id", "")
                uri = item.get("uri", "")
                name = item.get("name", "")
                artists = item.get("artists", [])
                artist_names = [a.get("name", "") for a in artists if a]
                album = item.get("album", {})
                album_name = album.get("name", "") if album else ""
                duration_ms = item.get("duration_ms", 0)
                duration_seconds = duration_ms // 1000
                explicit = item.get("explicit", False)
                isrc = None
                external_ids = item.get("external_ids", {})
                if external_ids:
                    isrc = external_ids.get("isrc")
                candidates.append(
                    SpotifyCandidate(
                        track_id=track_id,
                        uri=uri,
                        title=name,
                        artist_names=artist_names,
                        album=album_name,
                        duration_seconds=duration_seconds,
                        explicit=explicit,
                        isrc=isrc,
                    )
                )
            return candidates
        except SpotifyException as e:
            raise map_spotify_error(e, "search_tracks")

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
        cancel.raise_if_cancelled()
        try:
            # Get current user ID for owner
            user_info = self._client.me()
            if user_info is None:
                raise InvalidProviderResponse(
                    "spotify",
                    "create_playlist",
                    "Spotify returned null response for user identity"
                )
            user_id = user_info.get("id", "")
            if not user_id:
                raise InvalidProviderResponse(
                    "spotify",
                    "create_playlist",
                    "Spotify returned empty user ID for identity"
                )
            playlist = self._client.user_playlist_create(
                user=user_id,
                name=name,
                public=public,
                description=description,
            )
            if playlist is None:
                raise InvalidProviderResponse(
                    "spotify",
                    "create_playlist",
                    "Spotify returned null response for playlist creation"
                )
            playlist_id = playlist.get("id", "")
            playlist_name = playlist.get("name", name)
            owner_info = playlist.get("owner", {})
            owner = owner_info.get("id", user_id) if owner_info else user_id
            return PlaylistReference(
                provider="spotify",
                playlist_id=playlist_id,
                name=playlist_name,
                owner=owner,
            )
        except SpotifyException as e:
            raise map_spotify_error(e, "create_playlist")

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
        cancel.raise_if_cancelled()
        if not uris:
            return 0
        try:
            result = self._client.playlist_add_items(
                playlist_id=playlist_id,
                items=list(uris),
                position=position,
            )
            # Spotify's playlist_add_items returns a snapshot_id on success
            # The number of items added is the length of uris
            if result is not None:
                return len(uris)
            else:
                # If result is None, still return the count of URIs attempted
                return len(uris)
        except SpotifyException as e:
            raise map_spotify_error(e, "add_items")

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
        cancel.raise_if_cancelled()
        try:
            self._client.playlist_replace_items(
                playlist_id=playlist_id,
                items=list(uris),
            )
            return len(uris)
        except SpotifyException as e:
            raise map_spotify_error(e, "replace_items")

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
        cancel.raise_if_cancelled()
        try:
            results = self._client.playlist_items(
                playlist_id=playlist_id,
                limit=limit,
                offset=offset,
            )
            if results is None:
                return []
            items = results.get("items", [])
            candidates: List[SpotifyCandidate] = []
            for item in items:
                if item is None:
                    continue
                track = item.get("track")
                if track is None:
                    continue
                # Skip if track is None or missing required fields
                track_id = track.get("id", "")
                if not track_id:
                    continue
                uri = track.get("uri", "")
                name = track.get("name", "")
                artists = track.get("artists", [])
                artist_names = [a.get("name", "") for a in artists if a]
                album = track.get("album", {})
                album_name = album.get("name", "") if album else ""
                duration_ms = track.get("duration_ms", 0)
                duration_seconds = duration_ms // 1000
                explicit = track.get("explicit", False)
                isrc = None
                external_ids = track.get("external_ids", {})
                if external_ids:
                    isrc = external_ids.get("isrc")
                candidates.append(
                    SpotifyCandidate(
                        track_id=track_id,
                        uri=uri,
                        title=name,
                        artist_names=artist_names,
                        album=album_name,
                        duration_seconds=duration_seconds,
                        explicit=explicit,
                        isrc=isrc,
                    )
                )
            return candidates
        except SpotifyException as e:
            raise map_spotify_error(e, "read_items")

    def user_playlists(
        self,
        *,
        cancel: CancellationToken,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PlaylistReference]:
        """List the authenticated user's playlists.

        Args:
            cancel: CancellationToken to check for cancellation requests.
            limit: Maximum number of playlists to return. Defaults to 50.
            offset: Offset for pagination. Defaults to 0.

        Returns:
            List of PlaylistReference objects representing the user's playlists.
            May be empty if the user has no playlists or the offset exceeds the total.

        Raises:
            AuthenticationRequired: If the user is not authenticated with Spotify.
            PermissionDenied: If the user lacks permission to view their playlists.
            ProviderNotFound: If the Spotify API endpoint is not available.
            RateLimited: If the Spotify API rate limit has been exceeded.
            InvalidProviderResponse: If the provider returns malformed data.
            TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
            CancellationRequested: If the operation is cancelled via the token.
        """
        cancel.raise_if_cancelled()
        try:
            results = self._client.current_user_playlists(limit=limit, offset=offset)
            if results is None:
                return []
            items = results.get("items", [])
            playlists: List[PlaylistReference] = []
            for item in items:
                if item is None:
                    continue
                playlist_id = item.get("id", "")
                if not playlist_id:
                    continue
                name = item.get("name", "")
                owner_info = item.get("owner", {})
                owner = owner_info.get("id", "") if owner_info else ""
                playlists.append(
                    PlaylistReference(
                        provider="spotify",
                        playlist_id=playlist_id,
                        name=name,
                        owner=owner,
                    )
                )
            return playlists
        except SpotifyException as e:
            raise map_spotify_error(e, "user_playlists")


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
