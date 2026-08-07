"""Tests for Spotify provider utilities."""

import pytest

from playlist_bridge.providers.spotify import chunk_uris


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
