"""Persistence layer for playlist-bridge."""

from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.engine import create_engine_for_path

__all__ = ["Base", "create_engine_for_path"]
