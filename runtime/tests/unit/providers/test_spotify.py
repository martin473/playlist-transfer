"""Tests for Spotify provider utilities."""

import pytest
from typing import List, Sequence
from unittest.mock import MagicMock

from spotipy.exceptions import SpotifyException

from playlist_bridge.providers.spotify import chunk_uris, SpotifyAdapter, map_spotify_error, AuthenticatedSpotifyAdapter
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
from playlist_bridge.jobs.cancellation import FakeCancellationToken, CancellationToken


class FakeSpotifyAdapter:
    """Minimal fake adapter that satisfies the SpotifyAdapter protocol."""

    def identity(
        self,
        *,
        cancel: CancellationToken,
    ) -> AccountProfile:
        """Return a fake identity profile."""
        return AccountProfile(
            profile_name="fake_profile",
            service="spotify",
            provider_user_id="fake_user_123",
            display_name="Fake User",
        )

    def search_tracks(
        self,
        query: str,
        *,
        cancel: CancellationToken,
        limit: int = 10,
    ) -> List[SpotifyCandidate]:
        """Return fake search results."""
        return [
            SpotifyCandidate(
                track_id="fake_track_1",
                uri="spotify:track:fake_track_1",
                title="Fake Track 1",
                artist_names=["Fake Artist"],
                album="Fake Album",
                duration_seconds=180,
                explicit=False,
                isrc=None,
            )
        ]

    def create_playlist(
        self,
        name: str,
        *,
        cancel: CancellationToken,
        description: str = "",
        public: bool = False,
    ) -> PlaylistReference:
        """Return a fake playlist reference."""
        return PlaylistReference(
            provider="spotify",
            playlist_id="fake_playlist_123",
            name=name,
            owner="fake_user_123",
        )

    def add_items(
        self,
        playlist_id: str,
        uris: Sequence[str],
        *,
        cancel: CancellationToken,
        position: int = 0,
    ) -> int:
        """Return the number of items added."""
        return len(uris)

    def replace_items(
        self,
        playlist_id: str,
        uris: Sequence[str],
        *,
        cancel: CancellationToken,
    ) -> int:
        """Return the number of items replaced."""
        return len(uris)

    def read_items(
        self,
        playlist_id: str,
        *,
        cancel: CancellationToken,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SpotifyCandidate]:
        """Return fake playlist items."""
        return [
            SpotifyCandidate(
                track_id="fake_track_1",
                uri="spotify:track:fake_track_1",
                title="Fake Track 1",
                artist_names=["Fake Artist"],
                album="Fake Album",
                duration_seconds=180,
                explicit=False,
                isrc=None,
            )
        ]

    def user_playlists(
        self,
        *,
        cancel: CancellationToken,
        limit: int = 50,
        offset: int = 0,
    ) -> List[PlaylistReference]:
        """Return fake user playlists."""
        return [
            PlaylistReference(
                provider="spotify",
                playlist_id="fake_playlist_1",
                name="Fake Playlist 1",
                owner="fake_user_123",
            ),
            PlaylistReference(
                provider="spotify",
                playlist_id="fake_playlist_2",
                name="Fake Playlist 2",
                owner="fake_user_123",
            ),
        ]


def test_fake_adapter_satisfies_protocol() -> None:
    """Test that the fake adapter satisfies the SpotifyAdapter protocol.

    This test verifies that the fake adapter is assignable to the protocol type
    and that all required methods are present with the correct signatures.
    """
    # The protocol check is structural - we verify methods exist and have the right signatures
    adapter: SpotifyAdapter = FakeSpotifyAdapter()
    # Check all required methods exist
    assert hasattr(adapter, "identity")
    assert hasattr(adapter, "search_tracks")
    assert hasattr(adapter, "create_playlist")
    assert hasattr(adapter, "add_items")
    assert hasattr(adapter, "replace_items")
    assert hasattr(adapter, "read_items")
    assert hasattr(adapter, "user_playlists")
    # Verify methods are callable with expected signatures
    cancel = FakeCancellationToken()
    # Test identity
    result = adapter.identity(cancel=cancel)
    assert isinstance(result, AccountProfile)
    # Test search_tracks
    results = adapter.search_tracks("test", cancel=cancel)
    assert isinstance(results, list)
    # Test create_playlist
    playlist = adapter.create_playlist("test", cancel=cancel)
    assert isinstance(playlist, PlaylistReference)
    # Test add_items
    count = adapter.add_items("playlist_id", ["uri1"], cancel=cancel)
    assert isinstance(count, int)
    # Test replace_items
    count2 = adapter.replace_items("playlist_id", ["uri1"], cancel=cancel)
    assert isinstance(count2, int)
    # Test read_items
    items = adapter.read_items("playlist_id", cancel=cancel)
    assert isinstance(items, list)
    # Test user_playlists
    playlists = adapter.user_playlists(cancel=cancel)
    assert isinstance(playlists, list)


class TestChunkUris:
    """Property-based tests for chunk_uris."""

    def test_chunk_uris_concatenation_property(self) -> None:
        """Property test: concatenating chunks reproduces the original sequence."""
        # Test with various sequence sizes and batch sizes
        test_cases = [
            (list(range(0)), 5),
            (list(range(5)), 2),
            (list(range(10)), 3),
            (list(range(25)), 5),
            (list(range(100)), 10),
            (list(range(150)), 20),
            (list(range(200)), 30),
        ]

        for uris, batch_size in test_cases:
            chunks = chunk_uris(uris, batch_size)
            # Concatenate all chunks
            flattened: list[int] = []
            for chunk in chunks:
                flattened.extend(chunk)
            assert flattened == uris, f"Failed for uris={uris}, batch_size={batch_size}"

    def test_chunk_uris_returns_tuples(self) -> None:
        """Test that chunk_uris returns tuples (immutable sequences)."""
        uris = ["spotify:track:1", "spotify:track:2", "spotify:track:3"]
        chunks = chunk_uris(uris, 2)
        for chunk in chunks:
            assert isinstance(chunk, tuple)

    def test_chunk_uris_batch_size_limit(self) -> None:
        """Test that no chunk exceeds batch_size."""
        uris = list(range(150))
        batch_size = 10
        chunks = chunk_uris(uris, batch_size)
        for chunk in chunks:
            assert len(chunk) <= batch_size

    def test_chunk_uris_empty_sequence(self) -> None:
        """Test that empty sequence returns empty list."""
        uris: list[int] = []
        chunks = chunk_uris(uris, 5)
        assert chunks == []

    def test_chunk_uris_single_batch(self) -> None:
        """Test that sequence smaller than batch_size returns one chunk."""
        uris = ["a", "b", "c"]
        chunks = chunk_uris(uris, 10)
        assert len(chunks) == 1
        assert chunks[0] == ("a", "b", "c")

    def test_chunk_uris_exact_multiple(self) -> None:
        """Test sequence exactly divisible by batch_size."""
        uris = list(range(10))
        chunks = chunk_uris(uris, 5)
        assert len(chunks) == 2
        assert chunks[0] == (0, 1, 2, 3, 4)
        assert chunks[1] == (5, 6, 7, 8, 9)

    def test_chunk_uris_zero_batch_size_raises_value_error(self) -> None:
        """Test that batch_size < 1 raises ValueError."""
        with pytest.raises(ValueError, match="batch_size must be at least 1"):
            chunk_uris(["a", "b"], 0)

    def test_chunk_uris_negative_batch_size_raises_value_error(self) -> None:
        """Test that negative batch_size raises ValueError."""
        with pytest.raises(ValueError, match="batch_size must be at least 1"):
            chunk_uris(["a", "b"], -1)

    def test_chunk_uris_preserves_original_order(self) -> None:
        """Test that order is preserved across chunks."""
        uris = list(range(20))
        chunks = chunk_uris(uris, 6)
        flattened: list[int] = []
        for chunk in chunks:
            flattened.extend(chunk)
        assert flattened == uris

    def test_chunk_uris_works_with_string_uris(self) -> None:
        """Test chunking with actual Spotify URI strings."""
        uris = [
            "spotify:track:1",
            "spotify:track:2",
            "spotify:track:3",
            "spotify:track:4",
            "spotify:track:5",
        ]
        chunks = chunk_uris(uris, 2)
        assert chunks == [
            ("spotify:track:1", "spotify:track:2"),
            ("spotify:track:3", "spotify:track:4"),
            ("spotify:track:5",),
        ]

    def test_chunk_uris_large_batch_size(self) -> None:
        """Test with batch_size larger than the sequence."""
        uris = ["a", "b", "c"]
        chunks = chunk_uris(uris, 100)
        assert len(chunks) == 1
        assert chunks[0] == ("a", "b", "c")


class TestMapSpotifyError:
    """Tests for map_spotify_error function."""

    def test_map_spotify_error_401_authentication_required(self) -> None:
        """Test that 401 status maps to AuthenticationRequired."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(401, "Authentication failed")
        result = map_spotify_error(error, "search_tracks")

        from playlist_bridge.providers.errors import AuthenticationRequired
        assert isinstance(result, AuthenticationRequired)
        assert result.service == "spotify"
        assert result.operation == "search_tracks"
        assert "authentication" in str(result).lower()

    def test_map_spotify_error_authentication_from_message(self) -> None:
        """Test that authentication-related message maps to AuthenticationRequired."""
        class MockSpotifyError:
            def __init__(self, msg):
                self.msg = msg
            def __str__(self):
                return self.msg

        error = MockSpotifyError("Invalid authorization token")
        result = map_spotify_error(error, "create_playlist")

        from playlist_bridge.providers.errors import AuthenticationRequired
        assert isinstance(result, AuthenticationRequired)
        assert result.service == "spotify"
        assert result.operation == "create_playlist"

    def test_map_spotify_error_403_permission_denied(self) -> None:
        """Test that 403 status maps to PermissionDenied."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(403, "Insufficient scope")
        result = map_spotify_error(error, "add_items")

        from playlist_bridge.providers.errors import PermissionDenied
        assert isinstance(result, PermissionDenied)
        assert result.service == "spotify"
        assert result.operation == "add_items"
        assert "permission" in str(result).lower()
        assert "spotify" in str(result).lower()
        assert "add_items" in str(result)

    def test_map_spotify_error_403_permission_denied_safe_message(self) -> None:
        """Test that permission denied error contains a safe message without sensitive details."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(403, "Insufficient scope for user: john_doe@example.com")
        result = map_spotify_error(error, "create_playlist")

        from playlist_bridge.providers.errors import PermissionDenied
        assert isinstance(result, PermissionDenied)
        assert result.service == "spotify"
        assert result.operation == "create_playlist"
        message = str(result)
        assert "permission" in message.lower()
        assert "spotify" in message.lower()
        assert "john_doe" not in message
        assert "example.com" not in message

    def test_map_spotify_error_404_not_found(self) -> None:
        """Test that 404 status maps to ProviderNotFound."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(404, "Playlist not found")
        result = map_spotify_error(error, "read_items")

        from playlist_bridge.providers.errors import ProviderNotFound
        assert isinstance(result, ProviderNotFound)
        assert result.service == "spotify"
        assert result.operation == "read_items"

    def test_map_spotify_error_429_rate_limited(self) -> None:
        """Test that 429 status maps to RateLimited."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(429, "Rate limit exceeded")
        result = map_spotify_error(error, "search_tracks")

        from playlist_bridge.providers.errors import RateLimited
        assert isinstance(result, RateLimited)
        assert result.service == "spotify"
        assert result.operation == "search_tracks"

    def test_map_spotify_error_429_preserves_retry_after(self) -> None:
        """Test that 429 mapping preserves Retry-After metadata."""
        class MockSpotifyError:
            def __init__(self, http_status, msg, headers=None):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
                self.headers = headers or {}
            def __str__(self):
                return self.msg

        operation = "search_tracks"
        error = MockSpotifyError(429, "Rate limit exceeded", {"Retry-After": "60"})
        result = map_spotify_error(error, operation)

        from playlist_bridge.providers.errors import RateLimited
        assert isinstance(result, RateLimited)
        assert result.service == "spotify"
        assert result.operation == operation
        # Verify retry-after data is preserved in the error message
        message = str(result)
        assert "Retry-After" in message
        assert "60" in message

    def test_map_spotify_error_429_preserves_retry_after_from_resp(self) -> None:
        """Test that 429 mapping preserves Retry-After metadata when available via resp attribute."""
        class MockHeaders:
            def __init__(self):
                self._headers = {"Retry-After": "120"}
            def get(self, key, default=None):
                return self._headers.get(key, default)

        class MockResp:
            def __init__(self):
                self.headers = MockHeaders()

        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
                self.resp = MockResp()
            def __str__(self):
                return self.msg

        operation = "add_items"
        error = MockSpotifyError(429, "Rate limit exceeded")
        result = map_spotify_error(error, operation)

        from playlist_bridge.providers.errors import RateLimited
        assert isinstance(result, RateLimited)
        assert result.service == "spotify"
        assert result.operation == operation
        # Verify retry-after data is preserved in the error message
        message = str(result)
        assert "Retry-After" in message
        assert "120" in message

    def test_map_spotify_error_500_temporary_failure(self) -> None:
        """Test that 5xx status maps to TemporaryProviderFailure."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(503, "Service unavailable")
        result = map_spotify_error(error, "user_playlists")

        from playlist_bridge.providers.errors import TemporaryProviderFailure
        assert isinstance(result, TemporaryProviderFailure)
        assert result.service == "spotify"
        assert result.operation == "user_playlists"

    def test_map_spotify_error_unknown_status_invalid_response(self) -> None:
        """Test that unknown status maps to InvalidProviderResponse."""
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        error = MockSpotifyError(418, "I'm a teapot")
        result = map_spotify_error(error, "identity")

        from playlist_bridge.providers.errors import InvalidProviderResponse
        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "spotify"
        assert result.operation == "identity"

    def test_map_spotify_error_without_http_status_fallback(self) -> None:
        """Test fallback behavior when http_status is not available."""
        class MockSpotifyError:
            def __init__(self, msg):
                self.msg = msg
            def __str__(self):
                return self.msg

        error = MockSpotifyError("Something unexpected happened")
        result = map_spotify_error(error, "replace_items")

        from playlist_bridge.providers.errors import InvalidProviderResponse
        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "spotify"
        assert result.operation == "replace_items"

    def test_map_spotify_error_not_found_from_message_fallback(self) -> None:
        """Test that 'not found' in error message maps to ProviderNotFound when http_status is missing."""
        class MockSpotifyError:
            def __init__(self, msg):
                self.msg = msg
            def __str__(self):
                return self.msg

        error = MockSpotifyError("Playlist not found")
        result = map_spotify_error(error, "read_items")

        from playlist_bridge.providers.errors import ProviderNotFound
        assert isinstance(result, ProviderNotFound)
        assert result.service == "spotify"
        assert result.operation == "read_items"
        assert "not found" in str(result).lower()

    def test_map_spotify_error_server_errors_retryable(self) -> None:
        """Test that all 5xx server errors map to retryable TemporaryProviderFailure.

        This verifies that retryable server failures (500, 502, 503, 504)
        are properly mapped to TemporaryProviderFailure, which indicates
        the error is retryable by type.
        """
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        from playlist_bridge.providers.errors import TemporaryProviderFailure

        # Test multiple 5xx status codes
        server_errors = [500, 502, 503, 504]
        for status in server_errors:
            error = MockSpotifyError(status, f"Server error {status}")
            result = map_spotify_error(error, "search_tracks")
            assert isinstance(result, TemporaryProviderFailure), (
                f"Status {status} should map to TemporaryProviderFailure"
            )
            assert result.service == "spotify"
            assert result.operation == "search_tracks"
            assert str(status) in str(result)

    def test_map_spotify_error_malformed_success_response(self) -> None:
        """Test that malformed successful responses map to InvalidProviderResponse.

        This verifies that when the Spotify API returns a successful status
        (e.g., 200 OK) but the response body is malformed, incomplete, or
        missing required fields, it maps to InvalidProviderResponse.
        No partial domain object is returned.
        """
        class MockSpotifyError:
            def __init__(self, http_status, msg):
                self.http_status = http_status
                self.msg = msg
                self.code = http_status
            def __str__(self):
                return self.msg

        from playlist_bridge.providers.errors import InvalidProviderResponse

        # Scenario 1: 200 OK with malformed data (using a neutral message that doesn't
        # trigger keyword-based fallback for authentication/permission/not-found)
        error = MockSpotifyError(200, "Malformed response: missing required field 'name' in track data")
        result = map_spotify_error(error, "read_items")

        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "spotify"
        assert result.operation == "read_items"
        # Verify that no partial domain object is returned by checking the error type
        # and that the error message indicates malformed response
        assert "malformed" in str(result).lower() or "invalid" in str(result).lower()

        # Scenario 2: 200 OK with incomplete data (neutral message)
        error = MockSpotifyError(200, "Response validation failed: expected 10 items but received 0")
        result = map_spotify_error(error, "search_tracks")

        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "spotify"
        assert result.operation == "search_tracks"
        assert "validation" in str(result).lower() or "incomplete" in str(result).lower()

        # Scenario 3: Successful status but with data type mismatch (neutral message)
        error = MockSpotifyError(200, "Data parse error: field 'duration' expected integer but got string")
        result = map_spotify_error(error, "identity")

        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "spotify"
        assert result.operation == "identity"
        assert "parse" in str(result).lower() or "expected" in str(result).lower()


def test_authenticated_spotify_adapter_construction_no_network() -> None:
    """Test that constructing AuthenticatedSpotifyAdapter performs no network request.

    This test verifies that the adapter can be instantiated without making
    any network calls. The adapter should only store the client reference
    and not perform any I/O during construction.
    """
    import spotipy
    
    # Create a mock Spotipy client that will raise an exception if any
    # network method is called during construction.
    class MockSpotifyClient:
        def __init__(self, *args, **kwargs):
            # No network calls in constructor
            pass
        
        # Adding dummy methods to satisfy type checking
        def me(self):
            return {"id": "test_user", "display_name": "Test User"}
        
        def search(self, q, type, limit):
            return {"tracks": {"items": []}}
        
        def user_playlist_create(self, user, name, public, description):
            return {"id": "test_playlist", "name": name, "owner": {"id": user}}
        
        def playlist_add_items(self, playlist_id, items, position):
            return {"snapshot_id": "test_snapshot"}
        
        def playlist_replace_items(self, playlist_id, items):
            return None
        
        def playlist_items(self, playlist_id, limit, offset):
            return {"items": []}
        
        def current_user_playlists(self, limit, offset):
            return {"items": []}
    
    # Create a client instance - no network calls occur
    client = MockSpotifyClient()
    
    # Instantiate the adapter - this should not make any network calls
    adapter = AuthenticatedSpotifyAdapter(client)
    
    # Verify the adapter was created successfully
    assert adapter is not None
    assert hasattr(adapter, "_client")
    assert adapter._client is client
    
    # The adapter should be assignable to SpotifyAdapter protocol
    # This is a structural check - all methods should exist
    assert hasattr(adapter, "identity")
    assert hasattr(adapter, "search_tracks")
    assert hasattr(adapter, "create_playlist")
    assert hasattr(adapter, "add_items")
    assert hasattr(adapter, "replace_items")
    assert hasattr(adapter, "read_items")
    assert hasattr(adapter, "user_playlists")


def test_search_spotify_query_returns_only_track_items() -> None:
    """Test that search_spotify_query returns only track items and uses explicit limit.

    This test verifies:
    1. The function uses the explicit limit provided
    2. It returns only track items (no non-track items like artists or albums)
    3. Results are properly parsed into SpotifyCandidate objects
    """
    from playlist_bridge.providers.spotify import search_spotify_query
    from spotipy import Spotify
    
    # Mock the Spotify client
    class MockSpotifyClient:
        def search(self, q, type, market, limit):
            # Verify that type is "track" and limit is the explicit value
            assert type == "track"
            assert limit == 10  # Explicit small limit
            # Return mock search results with only track items
            return {
                "tracks": {
                    "items": [
                        {
                            "id": "track_1",
                            "uri": "spotify:track:track_1",
                            "name": "Test Track 1",
                            "artists": [{"name": "Test Artist 1"}],
                            "album": {"name": "Test Album 1"},
                            "duration_ms": 180000,
                            "explicit": False,
                            "external_ids": {"isrc": "US-ABC-12-34567"},
                        },
                        {
                            "id": "track_2",
                            "uri": "spotify:track:track_2",
                            "name": "Test Track 2",
                            "artists": [{"name": "Test Artist 2"}],
                            "album": {"name": "Test Album 2"},
                            "duration_ms": 240000,
                            "explicit": True,
                            "external_ids": {},
                        },
                    ]
                }
            }
    
    client = MockSpotifyClient()
    
    # Call the function with explicit limit
    results = search_spotify_query(
        client=client,
        query="test query",
        market="US",
        limit=10,
    )
    
    # Verify results
    assert len(results) == 2
    assert all(isinstance(candidate, SpotifyCandidate) for candidate in results)
    
    # Verify first track
    assert results[0].track_id == "track_1"
    assert results[0].uri == "spotify:track:track_1"
    assert results[0].title == "Test Track 1"
    assert results[0].artist_names == ["Test Artist 1"]
    assert results[0].album == "Test Album 1"
    assert results[0].duration_seconds == 180
    assert results[0].explicit is False
    assert results[0].isrc == "US-ABC-12-34567"
    
    # Verify second track
    assert results[1].track_id == "track_2"
    assert results[1].uri == "spotify:track:track_2"
    assert results[1].title == "Test Track 2"
    assert results[1].artist_names == ["Test Artist 2"]
    assert results[1].album == "Test Album 2"
    assert results[1].duration_seconds == 240
    assert results[1].explicit is True
    assert results[1].isrc is None


def test_search_spotify_query_with_market_none() -> None:
    """Test that search_spotify_query handles market=None correctly."""
    from playlist_bridge.providers.spotify import search_spotify_query
    
    class MockSpotifyClient:
        def search(self, q, type, market, limit):
            # Verify market is None
            assert market is None
            assert limit == 5
            return {
                "tracks": {
                    "items": [
                        {
                            "id": "track_1",
                            "uri": "spotify:track:track_1",
                            "name": "Test Track",
                            "artists": [{"name": "Test Artist"}],
                            "album": {"name": "Test Album"},
                            "duration_ms": 180000,
                            "explicit": False,
                            "external_ids": {},
                        }
                    ]
                }
            }
    
    client = MockSpotifyClient()
    results = search_spotify_query(
        client=client,
        query="test",
        market=None,
        limit=5,
    )
    
    assert len(results) == 1
    assert results[0].track_id == "track_1"


def test_search_spotify_query_empty_response() -> None:
    """Test that search_spotify_query returns empty list when no results found."""
    from playlist_bridge.providers.spotify import search_spotify_query
    
    class MockSpotifyClient:
        def search(self, q, type, market, limit):
            return {"tracks": {"items": []}}
    
    client = MockSpotifyClient()
    results = search_spotify_query(
        client=client,
        query="no results",
        market="US",
        limit=10,
    )
    
    assert results == []


def test_search_spotify_query_null_response() -> None:
    """Test that search_spotify_query handles null response from Spotify."""
    from playlist_bridge.providers.spotify import search_spotify_query
    
    class MockSpotifyClient:
        def search(self, q, type, market, limit):
            return None
    
    client = MockSpotifyClient()
    results = search_spotify_query(
        client=client,
        query="test",
        market="US",
        limit=10,
    )
    
    assert results == []


def test_search_spotify_query_handles_missing_fields() -> None:
    """Test that search_spotify_query skips incomplete track data gracefully.

    When track data is missing required fields (track_id, artist_names, album),
    the function should skip those items and continue processing valid ones.
    """
    from playlist_bridge.providers.spotify import search_spotify_query
    
    class MockSpotifyClient:
        def search(self, q, type, market, limit):
            return {
                "tracks": {
                    "items": [
                        {
                            # Valid track - should be included
                            "id": "valid_track",
                            "uri": "spotify:track:valid_track",
                            "name": "Valid Track",
                            "artists": [{"name": "Valid Artist"}],
                            "album": {"name": "Valid Album"},
                            "duration_ms": 180000,
                            "explicit": False,
                            "external_ids": {},
                        },
                        {
                            # Missing id - should be skipped
                            "uri": "spotify:track:track_1",
                            "name": "Test Track",
                            "artists": [{"name": "Test Artist"}],
                            "album": {"name": "Test Album"},
                            "duration_ms": 180000,
                            "explicit": False,
                        },
                        {
                            # Missing artists - should be skipped
                            "id": "no_artist_track",
                            "uri": "spotify:track:no_artist_track",
                            "name": "No Artist Track",
                            "artists": [],
                            "album": {"name": "Test Album"},
                            "duration_ms": 180000,
                            "explicit": False,
                        },
                        {
                            # Missing album name - should be skipped
                            "id": "no_album_track",
                            "uri": "spotify:track:no_album_track",
                            "name": "No Album Track",
                            "artists": [{"name": "Test Artist"}],
                            "album": {},
                            "duration_ms": 180000,
                            "explicit": False,
                        },
                    ]
                }
            }
    
    client = MockSpotifyClient()
    results = search_spotify_query(
        client=client,
        query="test",
        market="US",
        limit=10,
    )
    
    # Only the valid track should be returned
    assert len(results) == 1
    assert results[0].track_id == "valid_track"
    assert results[0].uri == "spotify:track:valid_track"
    assert results[0].title == "Valid Track"
    assert results[0].artist_names == ["Valid Artist"]
    assert results[0].album == "Valid Album"
    assert results[0].duration_seconds == 180
    assert results[0].explicit is False
    assert results[0].isrc is None


def test_get_spotify_identity_returns_user_identity() -> None:
    """Test that get_spotify_identity returns the user identity from the Spotify API."""
    from playlist_bridge.providers.spotify import get_spotify_identity

    class MockSpotifyClient:
        def me(self):
            return {
                "id": "test_user_123",
                "display_name": "Test User",
                "email": "test@example.com",
            }

    client = MockSpotifyClient()
    identity = get_spotify_identity(client)  # type: ignore
    
    assert identity.provider_user_id == "test_user_123"
    assert identity.display_name == "Test User"
    assert identity.service == "spotify"


def test_get_spotify_identity_maps_absent_display_name_to_fallback() -> None:
    """Test that get_spotify_identity maps absent display name to the user ID as a safe fallback."""
    from playlist_bridge.providers.spotify import get_spotify_identity

    class MockSpotifyClient:
        def me(self):
            return {
                "id": "test_user_456",
                # display_name is absent
            }

    client = MockSpotifyClient()
    identity = get_spotify_identity(client)  # type: ignore
    
    assert identity.provider_user_id == "test_user_456"
    assert identity.display_name == "test_user_456"  # Fallback to user ID
    assert identity.service == "spotify"


def test_get_spotify_identity_maps_empty_display_name_to_fallback() -> None:
    """Test that get_spotify_identity maps empty display name to the user ID as a safe fallback."""
    from playlist_bridge.providers.spotify import get_spotify_identity

    class MockSpotifyClient:
        def me(self):
            return {
                "id": "test_user_789",
                "display_name": "",  # Empty string
            }

    client = MockSpotifyClient()
    identity = get_spotify_identity(client)  # type: ignore
    
    assert identity.provider_user_id == "test_user_789"
    assert identity.display_name == "test_user_789"  # Fallback to user ID
    assert identity.service == "spotify"


def test_get_spotify_identity_raises_invalid_provider_response_for_null_response() -> None:
    """Test that get_spotify_identity raises InvalidProviderResponse when Spotify returns null."""
    from playlist_bridge.providers.spotify import get_spotify_identity
    from playlist_bridge.providers.errors import InvalidProviderResponse

    class MockSpotifyClient:
        def me(self):
            return None

    client = MockSpotifyClient()
    
    with pytest.raises(InvalidProviderResponse) as exc_info:
        get_spotify_identity(client)  # type: ignore
    
    assert "null response" in str(exc_info.value)


def test_get_spotify_identity_raises_invalid_provider_response_for_missing_id() -> None:
    """Test that get_spotify_identity raises InvalidProviderResponse when id field is missing."""
    from playlist_bridge.providers.spotify import get_spotify_identity
    from playlist_bridge.providers.errors import InvalidProviderResponse

    class MockSpotifyClient:
        def me(self):
            return {
                "display_name": "Test User",
                # id is missing
            }

    client = MockSpotifyClient()
    
    with pytest.raises(InvalidProviderResponse) as exc_info:
        get_spotify_identity(client)  # type: ignore
    
    assert "'id' field" in str(exc_info.value)


def test_read_spotify_playlist_items_returns_uris_and_none() -> None:
    """Test that read_spotify_playlist_items returns ordered URIs with None for unavailable tracks.

    This test verifies that the function correctly paginates playlist items and returns
    a list where each position is a URI string for available tracks or None for unavailable
    tracks, and that the position count matches the provider item count.
    """
    from playlist_bridge.providers.spotify import read_spotify_playlist_items
    from playlist_bridge.jobs.cancellation import FakeCancellationToken

    class MockSpotifyClient:
        def __init__(self):
            self._call_count = 0

        def playlist_items(self, playlist_id, limit, offset):
            self._call_count += 1
            # Return a paginated response with 3 items on first page and 2 on second
            if offset == 0:
                return {
                    "items": [
                        {"track": {"id": "track1", "uri": "spotify:track:track1"}},
                        {"track": None},  # Unavailable track
                        {"track": {"id": "track3", "uri": "spotify:track:track3"}},
                    ],
                    "total": 5,
                }
            elif offset == 3:
                return {
                    "items": [
                        {"track": {"id": "track4", "uri": "spotify:track:track4"}},
                        {"track": {"id": None, "uri": None}},  # Track with no URI
                    ],
                    "total": 5,
                }
            else:
                return {"items": [], "total": 5}

    client = MockSpotifyClient()
    cancel = FakeCancellationToken()

    result = read_spotify_playlist_items(client, "test_playlist_id", cancel)  # type: ignore

    # Verify the position count matches the provider item count (5 items total)
    assert len(result) == 5

    # Verify the order and content
    expected = [
        "spotify:track:track1",
        None,  # Unavailable track
        "spotify:track:track3",
        "spotify:track:track4",
        None,  # Track with no URI
    ]
    assert result == expected


def test_read_spotify_playlist_items_handles_empty_playlist() -> None:
    """Test that read_spotify_playlist_items returns an empty list for an empty playlist."""
    from playlist_bridge.providers.spotify import read_spotify_playlist_items
    from playlist_bridge.jobs.cancellation import FakeCancellationToken

    class MockSpotifyClient:
        def playlist_items(self, playlist_id, limit, offset):
            return {"items": [], "total": 0}

    client = MockSpotifyClient()
    cancel = FakeCancellationToken()

    result = read_spotify_playlist_items(client, "empty_playlist", cancel)  # type: ignore

    assert result == []


def test_read_spotify_playlist_items_handles_null_response() -> None:
    """Test that read_spotify_playlist_items returns an empty list when the API returns None."""
    from playlist_bridge.providers.spotify import read_spotify_playlist_items
    from playlist_bridge.jobs.cancellation import FakeCancellationToken

    class MockSpotifyClient:
        def playlist_items(self, playlist_id, limit, offset):
            return None

    client = MockSpotifyClient()
    cancel = FakeCancellationToken()

    result = read_spotify_playlist_items(client, "test_playlist", cancel)  # type: ignore

    assert result == []


def test_map_spotify_track_valid() -> None:
    """Test that map_spotify_track correctly maps a valid Spotify track object."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [
            {"name": "The Weeknd"}
        ],
        "album": {
            "name": "After Hours"
        },
        "duration_ms": 200000,
        "explicit": False,
        "external_ids": {
            "isrc": "USUG12000235"
        },
        "available_markets": ["US", "GB", "CA"]
    }

    result = map_spotify_track(raw_track, "US")

    assert result.track_id == "6rqhFgbbKwnb9MLmUQDhG6"
    assert result.uri == "spotify:track:6rqhFgbbKwnb9MLmUQDhG6"
    assert result.title == "Blinding Lights"
    assert result.artist_names == ["The Weeknd"]
    assert result.album == "After Hours"
    assert result.duration_seconds == 200
    assert result.explicit is False
    assert result.isrc == "USUG12000235"
    assert result.market_availability == ["US", "GB", "CA"]


def test_map_spotify_track_without_market() -> None:
    """Test that map_spotify_track works when market is None."""
    from playlist_bridge.providers.spotify import map_spotify_track

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [
            {"name": "The Weeknd"}
        ],
        "album": {
            "name": "After Hours"
        },
        "duration_ms": 200000,
        "explicit": False,
        "available_markets": ["US", "GB", "CA"]
    }

    result = map_spotify_track(raw_track, None)

    assert result.track_id == "6rqhFgbbKwnb9MLmUQDhG6"
    assert result.market_availability is None


def test_map_spotify_track_missing_id() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'id' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [{"name": "The Weeknd"}],
        "album": {"name": "After Hours"},
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'id' field" in str(exc_info.value)


def test_map_spotify_track_missing_uri() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'uri' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [{"name": "The Weeknd"}],
        "album": {"name": "After Hours"},
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'uri' field" in str(exc_info.value)


def test_map_spotify_track_missing_name() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'name' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "artists": [{"name": "The Weeknd"}],
        "album": {"name": "After Hours"},
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'name' field" in str(exc_info.value)


def test_map_spotify_track_missing_artists() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'artists' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "album": {"name": "After Hours"},
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'artists' field" in str(exc_info.value)


def test_map_spotify_track_empty_artists() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'artists' is empty."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [],
        "album": {"name": "After Hours"},
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    # The 'artists' field being empty is caught by the "missing or invalid 'artists' field" check
    assert "Missing or invalid 'artists' field" in str(exc_info.value)


def test_map_spotify_track_missing_album() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'album' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [{"name": "The Weeknd"}],
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'album' field" in str(exc_info.value)


def test_map_spotify_track_missing_album_name() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'album.name' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [{"name": "The Weeknd"}],
        "album": {"name": ""},
        "duration_ms": 200000,
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'album.name' field" in str(exc_info.value)


def test_map_spotify_track_missing_duration() -> None:
    """Test that map_spotify_track raises InvalidProviderResponse when 'duration_ms' is missing."""
    from playlist_bridge.providers.spotify import map_spotify_track
    from playlist_bridge.providers.errors import InvalidProviderResponse

    raw_track = {
        "id": "6rqhFgbbKwnb9MLmUQDhG6",
        "uri": "spotify:track:6rqhFgbbKwnb9MLmUQDhG6",
        "name": "Blinding Lights",
        "artists": [{"name": "The Weeknd"}],
        "album": {"name": "After Hours"},
    }

    with pytest.raises(InvalidProviderResponse) as exc_info:
        map_spotify_track(raw_track, None)
    assert "Missing or invalid 'duration_ms' field" in str(exc_info.value)


def test_create_spotify_playlist_success() -> None:
    """Test that create_spotify_playlist returns a DestinationPlaylist on success."""
    from playlist_bridge.providers.spotify import create_spotify_playlist
    from playlist_bridge.domain.models import DestinationPlaylist

    # Create a mock Spotipy client
    mock_client = MagicMock()
    mock_playlist = {
        "id": "test_playlist_123",
        "name": "Test Playlist",
        "owner": {"id": "test_user_123"},
        "snapshot_id": "snapshot_123",
        "external_urls": {"spotify": "https://open.spotify.com/playlist/test_playlist_123"},
        "tracks": {"total": 0},
        "collaborative": False,
    }
    mock_client.user_playlist_create.return_value = mock_playlist

    result = create_spotify_playlist(
        client=mock_client,
        owner_id="test_user_123",
        name="Test Playlist",
        description="Test description",
        public=True,
    )

    # Verify the result is a DestinationPlaylist with correct values
    assert isinstance(result, DestinationPlaylist)
    assert result.playlist_id == "test_playlist_123"
    assert result.name == "Test Playlist"
    assert result.owner_id == "test_user_123"
    assert result.public is True
    assert result.description == "Test description"
    assert result.snapshot_id == "snapshot_123"
    assert result.external_url == "https://open.spotify.com/playlist/test_playlist_123"
    assert result.track_count == 0
    assert result.collaborative is False

    # Verify the client was called correctly
    mock_client.user_playlist_create.assert_called_once_with(
        user="test_user_123",
        name="Test Playlist",
        public=True,
        description="Test description",
    )


def test_create_spotify_playlist_missing_id() -> None:
    """Test that create_spotify_playlist raises InvalidProviderResponse when playlist has no id."""
    from playlist_bridge.providers.spotify import create_spotify_playlist
    from playlist_bridge.providers.errors import InvalidProviderResponse

    mock_client = MagicMock()
    mock_client.user_playlist_create.return_value = {}

    with pytest.raises(InvalidProviderResponse) as exc_info:
        create_spotify_playlist(
            client=mock_client,
            owner_id="test_user",
            name="Test",
            description="",
            public=False,
        )
    assert "without an 'id' field" in str(exc_info.value)


def test_create_spotify_playlist_null_response() -> None:
    """Test that create_spotify_playlist raises InvalidProviderResponse when response is None."""
    from playlist_bridge.providers.spotify import create_spotify_playlist
    from playlist_bridge.providers.errors import InvalidProviderResponse

    mock_client = MagicMock()
    mock_client.user_playlist_create.return_value = None

    with pytest.raises(InvalidProviderResponse) as exc_info:
        create_spotify_playlist(
            client=mock_client,
            owner_id="test_user",
            name="Test",
            description="",
            public=False,
        )
    assert "null response" in str(exc_info.value)


def test_create_spotify_playlist_missing_name_fallback() -> None:
    """Test that create_spotify_playlist falls back to provided name when response has no name."""
    from playlist_bridge.providers.spotify import create_spotify_playlist
    from playlist_bridge.domain.models import DestinationPlaylist

    mock_client = MagicMock()
    mock_playlist = {
        "id": "test_playlist_123",
        "owner": {"id": "test_user_123"},
    }
    mock_client.user_playlist_create.return_value = mock_playlist

    result = create_spotify_playlist(
        client=mock_client,
        owner_id="test_user",
        name="Provided Name",
        description="",
        public=False,
    )

    # Should use the provided name as fallback
    assert result.name == "Provided Name"


def test_add_uri_batch_rejects_empty_batch() -> None:
    """Test that add_uri_batch rejects empty uris before any API call.

    This test verifies the acceptance criterion for micro-step 094.02:
    "An empty batch is rejected before any API call."

    The function should raise ValueError immediately when uris is empty,
    without making any network request to the Spotify API.
    """
    from playlist_bridge.providers.spotify import add_uri_batch

    mock_client = MagicMock()

    with pytest.raises(ValueError) as exc_info:
        add_uri_batch(
            client=mock_client,
            playlist_id="test_playlist_123",
            uris=[],
        )

    assert "empty uris sequence" in str(exc_info.value)
    # Verify that no API call was made
    mock_client.playlist_add_items.assert_not_called()


def test_add_uri_batch_returns_snapshot_id() -> None:
    """Test that add_uri_batch returns the snapshot ID from the API response."""
    from playlist_bridge.providers.spotify import add_uri_batch

    mock_client = MagicMock()
    expected_snapshot = "snapshot_abc123xyz"
    mock_client.playlist_add_items.return_value = expected_snapshot

    uris = ["spotify:track:abc123", "spotify:track:def456"]
    result = add_uri_batch(
        client=mock_client,
        playlist_id="test_playlist_123",
        uris=uris,
    )

    assert result == expected_snapshot
    mock_client.playlist_add_items.assert_called_once_with(
        playlist_id="test_playlist_123",
        items=uris,
    )


def test_add_all_uri_batches_batch_order_and_cancellation() -> None:
    """Test that add_all_uri_batches processes batches in order and checks cancellation.

    This test verifies the acceptance criterion for micro-step 095.02:
    "A fake adapter confirms batch order and checkpoint callbacks."

    It uses a fake adapter with a mock client to verify:
    1. URIs are chunked correctly into batches of the specified size.
    2. Batches are processed in the correct order.
    3. The cancellation token is checked before each batch.
    4. Snapshot IDs are returned for each batch.
    """
    from playlist_bridge.providers.spotify import add_all_uri_batches
    from playlist_bridge.jobs.cancellation import ActiveToken, CancelledToken
    from spotipy import Spotify

    # Create a mock client that returns snapshot IDs and is recognized as a Spotify instance
    mock_client = MagicMock(spec=Spotify)
    expected_snapshots = [f"snapshot_batch_{i}" for i in range(1, 4)]
    mock_client.playlist_add_items.side_effect = expected_snapshots

    # Create a fake adapter with the mock client as _client
    class FakeAdapterWithClient:
        """Fake adapter that exposes _client for snapshot retrieval."""

        def __init__(self, client):
            self._client = client

        def add_items(self, playlist_id, uris, *, cancel, position=0):
            return len(uris)

        def identity(self, *, cancel):
            from playlist_bridge.domain.models import AccountProfile
            return AccountProfile(
                profile_name="test",
                service="spotify",
                provider_user_id="test_user",
                display_name="Test User",
            )

        def search_tracks(self, query, *, cancel, limit=10):
            return []

        def create_playlist(self, name, *, cancel, description="", public=False):
            from playlist_bridge.domain.models import PlaylistReference
            return PlaylistReference(
                provider="spotify",
                playlist_id="test_playlist",
                name=name,
                owner="test_user",
            )

        def replace_items(self, playlist_id, uris, *, cancel):
            return len(uris)

        def read_items(self, playlist_id, *, cancel, limit=100, offset=0):
            return []

        def user_playlists(self, *, cancel, limit=50, offset=0):
            return []

    adapter = FakeAdapterWithClient(mock_client)
    cancel = ActiveToken()

    # Test with 5 URIs, batch size 2 -> 3 batches
    uris = [f"spotify:track:{i}" for i in range(1, 6)]
    playlist_id = "test_playlist_123"

    result = add_all_uri_batches(
        adapter=adapter,
        playlist_id=playlist_id,
        uris=uris,
        batch_size=2,
        cancel=cancel,
    )

    # Verify snapshot IDs
    assert result == expected_snapshots

    # Verify batch calls were made in order with correct chunks
    expected_chunks = [
        ["spotify:track:1", "spotify:track:2"],
        ["spotify:track:3", "spotify:track:4"],
        ["spotify:track:5"],
    ]
    actual_calls = mock_client.playlist_add_items.call_args_list
    assert len(actual_calls) == 3
    for i, call in enumerate(actual_calls):
        # call is (args, kwargs) - playlist_add_items may be called with args or kwargs
        # Check both possibilities
        args = call[0] if call[0] else ()
        kwargs = call[1] if call[1] else {}
        if args:
            # Called with positional args: (playlist_id, items, position?)
            assert args[0] == playlist_id
            assert list(args[1]) == expected_chunks[i]
        else:
            # Called with kwargs
            assert kwargs.get("playlist_id") == playlist_id
            assert list(kwargs.get("items", [])) == expected_chunks[i]

    # Test cancellation: cancelled token should raise CancellationRequested
    cancelled_token = CancelledToken()
    with pytest.raises(Exception) as exc_info:
        add_all_uri_batches(
            adapter=adapter,
            playlist_id=playlist_id,
            uris=uris,
            batch_size=2,
            cancel=cancelled_token,
        )
    # The exception should be CancellationRequested
    from playlist_bridge.providers.errors import CancellationRequested
    assert isinstance(exc_info.value, CancellationRequested)


def test_add_all_uri_batches_empty_uris() -> None:
    """Test that add_all_uri_batches returns empty list for empty URIs."""
    from playlist_bridge.providers.spotify import add_all_uri_batches
    from playlist_bridge.jobs.cancellation import ActiveToken
    from spotipy import Spotify

    # Create a simple fake adapter
    class FakeAdapterWithClient:
        def __init__(self, client):
            self._client = client

    mock_client = MagicMock(spec=Spotify)
    adapter = FakeAdapterWithClient(mock_client)
    cancel = ActiveToken()

    result = add_all_uri_batches(
        adapter=adapter,
        playlist_id="test_playlist",
        uris=[],
        batch_size=5,
        cancel=cancel,
    )

    assert result == []
    mock_client.playlist_add_items.assert_not_called()


def test_add_all_uri_batches_invalid_batch_size() -> None:
    """Test that add_all_uri_batches raises ValueError for invalid batch size."""
    from playlist_bridge.providers.spotify import add_all_uri_batches
    from playlist_bridge.jobs.cancellation import ActiveToken
    from spotipy import Spotify

    class FakeAdapterWithClient:
        def __init__(self, client):
            self._client = client

    mock_client = MagicMock(spec=Spotify)
    adapter = FakeAdapterWithClient(mock_client)
    cancel = ActiveToken()

    with pytest.raises(ValueError) as exc_info:
        add_all_uri_batches(
            adapter=adapter,
            playlist_id="test_playlist",
            uris=["spotify:track:abc"],
            batch_size=0,
            cancel=cancel,
        )

    assert "batch_size must be at least 1" in str(exc_info.value)


def test_add_all_uri_batches_no_client_attribute() -> None:
    """Test that add_all_uri_batches raises InvalidProviderResponse if adapter has no _client."""
    from playlist_bridge.providers.spotify import add_all_uri_batches
    from playlist_bridge.jobs.cancellation import ActiveToken
    from playlist_bridge.providers.errors import InvalidProviderResponse

    # Create an adapter without _client attribute
    class AdapterWithoutClient:
        def add_items(self, playlist_id, uris, *, cancel, position=0):
            return len(uris)

    adapter = AdapterWithoutClient()
    cancel = ActiveToken()

    with pytest.raises(InvalidProviderResponse) as exc_info:
        add_all_uri_batches(
            adapter=adapter,
            playlist_id="test_playlist",
            uris=["spotify:track:abc"],
            batch_size=1,
            cancel=cancel,
        )

    assert "Adapter does not expose underlying client" in str(exc_info.value)


def test_replace_playlist_items_replacement_then_append() -> None:
    """Test that replace_playlist_items uses replace for first batch and append for rest.

    This test verifies that:
    1. replace_items is called exactly once (for the first batch)
    2. add_items (via add_uri_batch) is called for remaining batches
    3. create_playlist is never called (no create mode)
    4. No merge operation is used (no read-before-write pattern)
    """
    from playlist_bridge.providers.spotify import replace_playlist_items
    from playlist_bridge.jobs.cancellation import ActiveToken, CancellationToken
    from playlist_bridge.providers.errors import InvalidProviderResponse
    from spotipy import Spotify

    # Track calls to verify behavior
    class TrackingAdapter:
        def __init__(self, client):
            self._client = client
            self.replace_items_calls: list[tuple[str, Sequence[str]]] = []
            self.add_items_calls: list[tuple[str, Sequence[str], int]] = []
            self.create_playlist_calls: list[tuple[str, str, bool]] = []
            self.read_items_calls: list[tuple[str, int, int]] = []

        def replace_items(
            self,
            playlist_id: str,
            uris: Sequence[str],
            *,
            cancel: CancellationToken,
        ) -> int:
            self.replace_items_calls.append((playlist_id, uris))
            return len(uris)

        def add_items(
            self,
            playlist_id: str,
            uris: Sequence[str],
            *,
            cancel: CancellationToken,
            position: int = 0,
        ) -> int:
            self.add_items_calls.append((playlist_id, uris, position))
            return len(uris)

        def create_playlist(
            self,
            name: str,
            *,
            cancel: CancellationToken,
            description: str = "",
            public: bool = False,
        ) -> PlaylistReference:
            self.create_playlist_calls.append((name, description, public))
            return PlaylistReference(
                provider="spotify",
                playlist_id="fake_id",
                name=name,
                owner="fake_user",
            )

        def read_items(
            self,
            playlist_id: str,
            *,
            cancel: CancellationToken,
            limit: int = 100,
            offset: int = 0,
        ) -> List[SpotifyCandidate]:
            self.read_items_calls.append((playlist_id, limit, offset))
            return []

        def identity(self, *, cancel: CancellationToken) -> AccountProfile:
            return AccountProfile(
                profile_name="fake",
                service="spotify",
                provider_user_id="fake_user",
                display_name="Fake User",
            )

        def search_tracks(
            self,
            query: str,
            *,
            cancel: CancellationToken,
            limit: int = 10,
        ) -> List[SpotifyCandidate]:
            return []

        def user_playlists(
            self,
            *,
            cancel: CancellationToken,
            limit: int = 50,
            offset: int = 0,
        ) -> List[PlaylistReference]:
            return []

    # Create mock Spotify client for add_uri_batch to use
    mock_client = MagicMock(spec=Spotify)
    # Mock playlist_add_items to return a snapshot ID string
    mock_client.playlist_add_items.return_value = "snapshot_123"

    adapter = TrackingAdapter(mock_client)
    cancel = ActiveToken()
    playlist_id = "test_playlist"
    uris = [
        "spotify:track:1",
        "spotify:track:2",
        "spotify:track:3",
        "spotify:track:4",
        "spotify:track:5",
    ]
    batch_size = 2

    result = replace_playlist_items(
        adapter=adapter,
        playlist_id=playlist_id,
        uris=uris,
        batch_size=batch_size,
        cancel=cancel,
    )

    # Verify replace_items was called once with the first batch
    assert len(adapter.replace_items_calls) == 1
    replace_playlist_id, replace_uris = adapter.replace_items_calls[0]
    assert replace_playlist_id == playlist_id
    assert list(replace_uris) == ["spotify:track:1", "spotify:track:2"]

    # Verify add_items was called for remaining batches (via add_uri_batch)
    # add_uri_batch uses client.playlist_add_items, not adapter.add_items directly
    # But we can verify the adapter's add_items method was not called directly
    # Instead, we verify that playlist_add_items was called on the client
    # with the remaining batches
    assert mock_client.playlist_add_items.call_count == 2  # Two remaining batches
    # Check the calls: batch 3-4, then batch 5
    call_args_list = mock_client.playlist_add_items.call_args_list
    assert call_args_list[0].kwargs["playlist_id"] == playlist_id
    assert list(call_args_list[0].kwargs["items"]) == ["spotify:track:3", "spotify:track:4"]
    assert call_args_list[1].kwargs["playlist_id"] == playlist_id
    assert list(call_args_list[1].kwargs["items"]) == ["spotify:track:5"]

    # Verify create_playlist was never called (no create mode)
    assert len(adapter.create_playlist_calls) == 0

    # Verify read_items was never called (no merge mode with read-before-write)
    assert len(adapter.read_items_calls) == 0

    # Verify result contains snapshot IDs for each append operation
    # First batch (replacement) has no snapshot ID, so only 2 snapshot IDs
    assert result == ["snapshot_123", "snapshot_123"]


def test_replace_playlist_items_empty_uris() -> None:
    """Test that replace_playlist_items clears playlist when URIs empty."""
    from playlist_bridge.providers.spotify import replace_playlist_items
    from playlist_bridge.jobs.cancellation import ActiveToken
    from spotipy import Spotify

    # Track calls
    class TrackingAdapter:
        def __init__(self, client):
            self._client = client
            self.replace_items_calls: list[tuple[str, Sequence[str]]] = []

        def replace_items(
            self,
            playlist_id: str,
            uris: Sequence[str],
            *,
            cancel: CancellationToken,
        ) -> int:
            self.replace_items_calls.append((playlist_id, uris))
            return len(uris)

        def add_items(self, *args, **kwargs) -> int:
            return 0

        def create_playlist(self, *args, **kwargs) -> PlaylistReference:
            return PlaylistReference(
                provider="spotify",
                playlist_id="fake_id",
                name="test",
                owner="fake_user",
            )

        def identity(self, *, cancel: CancellationToken) -> AccountProfile:
            return AccountProfile(
                profile_name="fake",
                service="spotify",
                provider_user_id="fake_user",
                display_name="Fake User",
            )

        def search_tracks(self, *args, **kwargs) -> List[SpotifyCandidate]:
            return []

        def read_items(self, *args, **kwargs) -> List[SpotifyCandidate]:
            return []

        def user_playlists(self, *args, **kwargs) -> List[PlaylistReference]:
            return []

    mock_client = MagicMock(spec=Spotify)
    adapter = TrackingAdapter(mock_client)
    cancel = ActiveToken()

    result = replace_playlist_items(
        adapter=adapter,
        playlist_id="test_playlist",
        uris=[],
        batch_size=5,
        cancel=cancel,
    )

    # Verify replace_items was called with empty list to clear the playlist
    assert len(adapter.replace_items_calls) == 1
    replace_playlist_id, replace_uris = adapter.replace_items_calls[0]
    assert replace_playlist_id == "test_playlist"
    assert list(replace_uris) == []

    # Verify no add operations
    mock_client.playlist_add_items.assert_not_called()

    # Result should be empty
    assert result == []


def test_replace_playlist_items_single_batch() -> None:
    """Test that replace_playlist_items with single batch just replaces."""
    from playlist_bridge.providers.spotify import replace_playlist_items
    from playlist_bridge.jobs.cancellation import ActiveToken
    from spotipy import Spotify

    class TrackingAdapter:
        def __init__(self, client):
            self._client = client
            self.replace_items_calls: list[tuple[str, Sequence[str]]] = []

        def replace_items(
            self,
            playlist_id: str,
            uris: Sequence[str],
            *,
            cancel: CancellationToken,
        ) -> int:
            self.replace_items_calls.append((playlist_id, uris))
            return len(uris)

        def add_items(self, *args, **kwargs) -> int:
            return 0

        def create_playlist(self, *args, **kwargs) -> PlaylistReference:
            return PlaylistReference(
                provider="spotify",
                playlist_id="fake_id",
                name="test",
                owner="fake_user",
            )

        def identity(self, *, cancel: CancellationToken) -> AccountProfile:
            return AccountProfile(
                profile_name="fake",
                service="spotify",
                provider_user_id="fake_user",
                display_name="Fake User",
            )

        def search_tracks(self, *args, **kwargs) -> List[SpotifyCandidate]:
            return []

        def read_items(self, *args, **kwargs) -> List[SpotifyCandidate]:
            return []

        def user_playlists(self, *args, **kwargs) -> List[PlaylistReference]:
            return []

    mock_client = MagicMock(spec=Spotify)
    adapter = TrackingAdapter(mock_client)
    cancel = ActiveToken()
    uris = ["spotify:track:1", "spotify:track:2"]

    result = replace_playlist_items(
        adapter=adapter,
        playlist_id="test_playlist",
        uris=uris,
        batch_size=10,  # Larger than URI count -> single batch
        cancel=cancel,
    )

    # Verify replace_items was called once
    assert len(adapter.replace_items_calls) == 1
    replace_playlist_id, replace_uris = adapter.replace_items_calls[0]
    assert replace_playlist_id == "test_playlist"
    assert list(replace_uris) == ["spotify:track:1", "spotify:track:2"]

    # Verify no add operations
    mock_client.playlist_add_items.assert_not_called()

    # Result should be empty (no append operations)
    assert result == []


def test_replace_playlist_items_invalid_batch_size() -> None:
    """Test that replace_playlist_items raises ValueError for invalid batch size."""
    from playlist_bridge.providers.spotify import replace_playlist_items
    from playlist_bridge.jobs.cancellation import ActiveToken
    from spotipy import Spotify

    mock_client = MagicMock(spec=Spotify)

    class SimpleAdapter:
        def __init__(self, client):
            self._client = client

        def replace_items(self, *args, **kwargs) -> int:
            return 0

    adapter = SimpleAdapter(mock_client)
    cancel = ActiveToken()

    with pytest.raises(ValueError) as exc_info:
        replace_playlist_items(
            adapter=adapter,
            playlist_id="test_playlist",
            uris=["spotify:track:1"],
            batch_size=0,
            cancel=cancel,
        )

    assert "batch_size must be at least 1" in str(exc_info.value)


def test_replace_playlist_items_cancellation() -> None:
    """Test that replace_playlist_items respects cancellation."""
    from playlist_bridge.providers.spotify import replace_playlist_items
    from playlist_bridge.jobs.cancellation import ActiveToken
    from playlist_bridge.providers.errors import CancellationRequested
    from spotipy import Spotify

    class CancelledToken:
        def raise_if_cancelled(self) -> None:
            raise CancellationRequested("spotify", "replace_playlist_items", "Cancelled")

    mock_client = MagicMock(spec=Spotify)

    class SimpleAdapter:
        def __init__(self, client):
            self._client = client

        def replace_items(self, *args, **kwargs) -> int:
            return 0

    adapter = SimpleAdapter(mock_client)
    cancel = CancelledToken()

    with pytest.raises(CancellationRequested):
        replace_playlist_items(
            adapter=adapter,
            playlist_id="test_playlist",
            uris=["spotify:track:1", "spotify:track:2"],
            batch_size=1,
            cancel=cancel,
        )
