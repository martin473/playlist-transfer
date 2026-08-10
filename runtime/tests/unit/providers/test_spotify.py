"""Tests for Spotify provider utilities."""

import pytest
from typing import List, Sequence

from playlist_bridge.providers.spotify import chunk_uris, SpotifyAdapter
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
