"""Repository functions for playlist-bridge persistence."""

from sqlalchemy.orm import Session

from playlist_bridge.persistence.models import MatchCacheEntry


def lookup_match_cache(session: Session, fingerprint: str) -> MatchCacheEntry | None:
    """Look up one automatic match by canonical fingerprint.

    Args:
        session: SQLAlchemy Session instance.
        fingerprint: Canonical source track fingerprint string.

    Returns:
        MatchCacheEntry if found, else None.
    """
    return session.query(MatchCacheEntry).filter_by(source_fingerprint=fingerprint).first()
