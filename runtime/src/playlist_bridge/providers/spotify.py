"""Spotify provider utilities."""

from typing import Sequence


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
