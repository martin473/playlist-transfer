"""SQLAlchemy ORM models for playlist-bridge persistence."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Integer, String, Text, types, UniqueConstraint, Index, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from playlist_bridge.persistence.base import Base


class JobRecord(Base):
    """Core jobs table storing transfer job state and checkpoints.

    This model represents a transfer job with its request parameters,
    current state, source/destination references, checkpoint counters,
    timestamps, and error information.
    """

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    request_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_playlist_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    destination_playlist_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    source_track_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    match_checkpoint: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    write_checkpoint: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    verification_checkpoint: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(types.DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lease_holder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    lease_expires_at: Mapped[Optional[datetime]] = mapped_column(types.DateTime(timezone=True), nullable=True)
    lease_heartbeat_at: Mapped[Optional[datetime]] = mapped_column(types.DateTime(timezone=True), nullable=True)
    lease_token_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        return f"<JobRecord id={self.id} state={self.state}>"


class AccountProfileRecord(Base):
    """Account profile table storing provider account information.

    This model represents a user account profile for a specific service provider
    (e.g., Spotify, YouTube). It stores the profile name, service type,
    provider user ID, display name, and timestamps.

    A unique constraint ensures that the same (service, profile_name) pair
    cannot be inserted twice.
    """

    __tablename__ = "account_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    profile_name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    __table_args__ = (
        # Unique constraint on (service, profile_name) ensures no duplicate pairs
        UniqueConstraint("service", "profile_name", name="uq_service_profile_name"),
    )

class MatchCacheEntry(Base):
    """Match cache table storing verified match results.

    This model represents a canonical mapping from a source track fingerprint
    to a Spotify track ID, with confidence, origin, and last verification timestamp.
    The fingerprint is unique and supports an indexed lookup.
    """

    __tablename__ = "match_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    spotify_track_id: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    origin: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    last_verified_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    created_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    __table_args__ = (
        UniqueConstraint("source_fingerprint", name="uq_match_cache_source_fingerprint"),
        Index("ix_match_cache_source_fingerprint", "source_fingerprint"),
    )

    def __repr__(self) -> str:
        return f"<MatchCacheEntry fingerprint={self.source_fingerprint} spotify_id={self.spotify_track_id}>"


class ManualCorrection(Base):
    """Manual corrections table storing explicit source fingerprint to Spotify ID or skip decisions.

    This model represents a user-provided correction that maps a source track fingerprint
    to either a Spotify track ID (for accepted matches) or a skip indicator (for rejected tracks).
    A newer correction replaces the prior correction for the same fingerprint.

    The table stores the fingerprint, the resolution (spotify_track_id or skip_reason),
    an optional explanation, the source of the correction, and timestamps.
    """

    __tablename__ = "manual_corrections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    spotify_track_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    skip_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origin: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    __table_args__ = (
        UniqueConstraint("source_fingerprint", name="uq_manual_corrections_source_fingerprint"),
        Index("ix_manual_corrections_source_fingerprint", "source_fingerprint"),
    )

    def __repr__(self) -> str:
        if self.spotify_track_id:
            return f"<ManualCorrection fingerprint={self.source_fingerprint} spotify_id={self.spotify_track_id}>"
        else:
            return f"<ManualCorrection fingerprint={self.source_fingerprint} skip={self.skip_reason}>"


class SourceTrackRecord(Base):
    """Source tracks table storing raw source items for a transfer job.

    This model represents a source track from a playlist, keyed by job ID and
    source item ID. It stores the source position and normalized fields from
    the domain SourceTrack model.

    A unique constraint prevents duplicate source items within one job.
    """

    __tablename__ = "source_tracks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    source_item_id: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    artist_names: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    video_id: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    __table_args__ = (
        UniqueConstraint("job_id", "source_item_id", name="uq_source_tracks_job_item"),
        Index("ix_source_tracks_source_item_id", "source_item_id"),
    )

    def __repr__(self) -> str:
        return f"<SourceTrackRecord job_id={self.job_id} source_item_id={self.source_item_id} position={self.position}>"


class MatchDecisionRecord(Base):
    """Match decisions table storing per-track match decisions for each job.

    This model represents a decision for a source track in a transfer job,
    storing the selected Spotify ID, match score data, decision status,
    and a reviewed flag.

    A decision can be replaced atomically using upsert semantics.
    """

    __tablename__ = "match_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    source_item_id: Mapped[str] = mapped_column(String(255), nullable=False)
    spotify_track_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    score_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    decision_status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    reviewed: Mapped[bool] = mapped_column(types.Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        types.DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )

    __table_args__ = (
        UniqueConstraint("job_id", "source_item_id", name="uq_match_decisions_job_item"),
        Index("ix_match_decisions_job_item", "job_id", "source_item_id"),
        Index("ix_match_decisions_decision_status", "decision_status"),
    )

    def __repr__(self) -> str:
        return f"<MatchDecisionRecord job_id={self.job_id} source_item_id={self.source_item_id} status={self.decision_status}>"
