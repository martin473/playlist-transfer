"""SQLAlchemy ORM models for playlist-bridge persistence."""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Integer, String, Text, types, UniqueConstraint
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

    def __repr__(self) -> str:
        return f"<AccountProfileRecord service={self.service} profile_name={self.profile_name}>"
