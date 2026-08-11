"""Tests for Spotify provider utilities."""

import pytest
from typing import List, Sequence

from spotipy.exceptions import SpotifyException

from playlist_bridge.providers.spotify import chunk_uris, SpotifyAdapter, map_spotify_error
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
