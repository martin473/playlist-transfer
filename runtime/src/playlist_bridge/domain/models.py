"""Domain models for the playlist bridge."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from playlist_bridge.domain.enums import MatchPolicy, TransferMode


class SpotifyCandidate(BaseModel):
    """A Spotify track candidate for matching against source items.

    Attributes:
        track_id: Spotify track ID (e.g., "6rqhFgbbKwnb9MLmUQDhG6")
        uri: Spotify track URI (e.g., "spotify:track:6rqhFgbbKwnb9MLmUQDhG6")
        title: Track title
        artist_names: List of artist names
        album: Album name
        duration_seconds: Track duration in seconds
        explicit: Whether the track is explicit
        isrc: Optional International Standard Recording Code
        market_availability: Optional list of markets where the track is available
    """

    track_id: str = Field(description="Spotify track ID")
    uri: str = Field(description="Spotify track URI (e.g., spotify:track:...)")
    title: str = Field(description="Track title")
    artist_names: list[str] = Field(description="List of artist names")
    album: str = Field(description="Album name")
    duration_seconds: int = Field(description="Track duration in seconds", ge=0)
    explicit: bool = Field(description="Whether the track is explicit")
    isrc: Optional[str] = Field(default=None, description="International Standard Recording Code")
    market_availability: Optional[list[str]] = Field(
        default=None,
        description="List of markets where the track is available (ISO 3166-1 alpha-2 codes)",
    )

    @field_validator("uri")
    @classmethod
    def validate_uri(cls, v: str) -> str:
        """Validate that the URI is a Spotify track URI."""
        if not v.startswith("spotify:track:"):
            raise ValueError("URI must start with 'spotify:track:'")
        return v

    @field_validator("track_id")
    @classmethod
    def validate_track_id(cls, v: str) -> str:
        """Validate that the track ID is not empty."""
        if not v:
            raise ValueError("Track ID cannot be empty")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that the title is not empty."""
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("artist_names")
    @classmethod
    def validate_artist_names(cls, v: list[str]) -> list[str]:
        """Validate that artist names list is not empty."""
        if not v:
            raise ValueError("Artist names cannot be empty")
        return v

    @field_validator("album")
    @classmethod
    def validate_album(cls, v: str) -> str:
        """Validate that the album name is not empty."""
        if not v:
            raise ValueError("Album cannot be empty")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourceTrack(BaseModel):
    """A track from a source playlist (e.g., YouTube).

    This model represents a single item in a source playlist, with position
    and metadata, without exposing provider-specific details or credentials.

    Attributes:
        position: Position in the playlist (0-indexed, strictly ascending).
        title: Track title.
        artist_names: List of artist or channel names.
        duration_seconds: Track duration in seconds.
        video_id: Source video ID (e.g., YouTube video ID).
        channel_title: Optional channel title of the uploader.
    """

    model_config = {"extra": "forbid"}

    position: int = Field(description="Position in the playlist (0-indexed)", ge=0)
    title: str = Field(description="Track title")
    artist_names: list[str] = Field(description="List of artist or channel names")
    duration_seconds: int = Field(description="Track duration in seconds", ge=0)
    video_id: str = Field(description="Source video ID")
    channel_title: Optional[str] = Field(
        default=None,
        description="Optional channel title of the uploader",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v

    @field_validator("artist_names")
    @classmethod
    def validate_artist_names(cls, v: list[str]) -> list[str]:
        """Validate that artist_names is not empty."""
        if not v:
            raise ValueError("artist_names cannot be empty")
        return v

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, v: str) -> str:
        """Validate that video_id is not empty."""
        if not v or not v.strip():
            raise ValueError("video_id cannot be empty")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class LoadedSourcePlaylist(BaseModel):
    """A fully loaded source playlist with metadata and ordered tracks.

    This model represents a playlist loaded from a source service (e.g., YouTube)
    with all tracks ordered by position. Tracks must be in strictly ascending
    position order.

    Attributes:
        metadata: Metadata about the playlist.
        tracks: List of tracks in ascending position order.
    """

    model_config = {"extra": "forbid"}

    metadata: SourcePlaylistMetadata = Field(description="Playlist metadata")
    tracks: list[SourceTrack] = Field(description="Tracks in ascending position order")

    @model_validator(mode="after")
    def validate_track_positions(self) -> "LoadedSourcePlaylist":
        """Validate that tracks are in strictly ascending position order."""
        if not self.tracks:
            return self

        positions = [track.position for track in self.tracks]
        # Check for strictly ascending order (no duplicates, no descending)
        for i in range(len(positions) - 1):
            if positions[i] >= positions[i + 1]:
                raise ValueError(
                    f"Tracks must be in strictly ascending position order: "
                    f"position {positions[i]} >= {positions[i + 1]} at index {i}"
                )

        return self

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourcePlaylistMetadata(BaseModel):
    """A provider-neutral source playlist metadata model.

    This model represents metadata for a playlist from a source service (e.g., YouTube)
    without exposing provider-specific details or credentials.

    Attributes:
        reference: Playlist reference (e.g., URL or ID in the source system).
        description: Optional description of the playlist.
        privacy_status: Optional privacy status (e.g., "public", "private", "unlisted").
        owner_channel_id: Optional channel ID of the playlist owner.
        owner_channel_title: Optional channel title of the playlist owner.
        item_count: Number of items in the playlist (non-negative).
    """

    model_config = {"extra": "forbid"}

    reference: str = Field(description="Playlist reference (e.g., URL or ID in the source system)")
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the playlist",
    )
    privacy_status: Optional[str] = Field(
        default=None,
        description="Optional privacy status (e.g., 'public', 'private', 'unlisted')",
    )
    owner_channel_id: Optional[str] = Field(
        default=None,
        description="Optional channel ID of the playlist owner",
    )
    owner_channel_title: Optional[str] = Field(
        default=None,
        description="Optional channel title of the playlist owner",
    )
    item_count: int = Field(
        description="Number of items in the playlist",
        ge=0,
    )

    @field_validator("reference")
    @classmethod
    def validate_reference(cls, v: str) -> str:
        """Validate that reference is not empty."""
        if not v or not v.strip():
            raise ValueError("reference cannot be empty")
        return v

    @field_validator("item_count")
    @classmethod
    def validate_item_count(cls, v: int) -> int:
        """Validate that item_count is non-negative."""
        if v < 0:
            raise ValueError("item_count cannot be negative")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourceTrack(BaseModel):
    """A track from a source playlist (e.g., YouTube).

    This model represents a single item in a source playlist, with position
    and metadata, without exposing provider-specific details or credentials.

    Attributes:
        position: Position in the playlist (0-indexed, strictly ascending).
        title: Track title.
        artist_names: List of artist or channel names.
        duration_seconds: Track duration in seconds.
        video_id: Source video ID (e.g., YouTube video ID).
        channel_title: Optional channel title of the uploader.
    """

    model_config = {"extra": "forbid"}

    position: int = Field(description="Position in the playlist (0-indexed)", ge=0)
    title: str = Field(description="Track title")
    artist_names: list[str] = Field(description="List of artist or channel names")
    duration_seconds: int = Field(description="Track duration in seconds", ge=0)
    video_id: str = Field(description="Source video ID")
    channel_title: Optional[str] = Field(
        default=None,
        description="Optional channel title of the uploader",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v

    @field_validator("artist_names")
    @classmethod
    def validate_artist_names(cls, v: list[str]) -> list[str]:
        """Validate that artist_names is not empty."""
        if not v:
            raise ValueError("artist_names cannot be empty")
        return v

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, v: str) -> str:
        """Validate that video_id is not empty."""
        if not v or not v.strip():
            raise ValueError("video_id cannot be empty")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class LoadedSourcePlaylist(BaseModel):
    """A fully loaded source playlist with metadata and ordered tracks.

    This model represents a playlist loaded from a source service (e.g., YouTube)
    with all tracks ordered by position. Tracks must be in strictly ascending
    position order.

    Attributes:
        metadata: Metadata about the playlist.
        tracks: List of tracks in ascending position order.
    """

    model_config = {"extra": "forbid"}

    metadata: SourcePlaylistMetadata = Field(description="Playlist metadata")
    tracks: list[SourceTrack] = Field(description="Tracks in ascending position order")

    @model_validator(mode="after")
    def validate_track_positions(self) -> "LoadedSourcePlaylist":
        """Validate that tracks are in strictly ascending position order."""
        if not self.tracks:
            return self

        positions = [track.position for track in self.tracks]
        # Check for strictly ascending order (no duplicates, no descending)
        for i in range(len(positions) - 1):
            if positions[i] >= positions[i + 1]:
                raise ValueError(
                    f"Tracks must be in strictly ascending position order: "
                    f"position {positions[i]} >= {positions[i + 1]} at index {i}"
                )

        return self

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class MatchScore(BaseModel):
    """A score representing the quality of a match between a source track and a Spotify candidate.

    The match score is composed of multiple component scores and penalties, which are
    combined into a total score. Each component and penalty is constrained to a
    documented numeric range.

    Attributes:
        title_similarity: Similarity score for the title (0.0 to 1.0).
        artist_similarity: Similarity score for artist names (0.0 to 1.0).
        duration_similarity: Similarity score for duration (0.0 to 1.0).
        version_agreement: Agreement score for version indicators (0.0 to 1.0).
        unwanted_version_penalty: Penalty for unwanted version indicators (0.0 to 1.0).
        explicit_state: Score for explicit status match (0.0 to 1.0).
        total_score: Combined total score (0.0 to 1.0).
        reasons: Explanatory reasons for the score components.
    """

    title_similarity: float = Field(
        description="Similarity score for the title (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    artist_similarity: float = Field(
        description="Similarity score for artist names (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    duration_similarity: float = Field(
        description="Similarity score for duration (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    version_agreement: float = Field(
        description="Agreement score for version indicators (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    unwanted_version_penalty: float = Field(
        description="Penalty for unwanted version indicators (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    explicit_state: float = Field(
        description="Score for explicit status match (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    total_score: float = Field(
        description="Combined total score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    reasons: list[str] = Field(
        default_factory=list,
        description="Explanatory reasons for the score components",
    )

    @field_validator("reasons", mode="before")
    @classmethod
    def validate_reasons(cls, v: list[str]) -> list[str]:
        """Validate that reasons are not empty or whitespace-only strings."""
        if v is None:
            return []
        for reason in v:
            if not reason or not reason.strip():
                raise ValueError("Reason strings cannot be empty or whitespace only")
        return v

    @model_validator(mode="after")
    def validate_consistency(self) -> "MatchScore":
        """Validate that the total score is consistent with components."""
        # The total score should be roughly consistent with the average of components.
        # We don't enforce exact equality because weights may be applied.
        # Instead, ensure total_score is within the range of 0.0 to 1.0.
        if not (0.0 <= self.total_score <= 1.0):
            raise ValueError("total_score must be between 0.0 and 1.0")
        return self


class MatchDecision(BaseModel):
    """A decision for matching a source track to a Spotify candidate.

    Attributes:
        source_item_id: ID of the source track.
        status: Match status (matched, unmatched, review).
        selected_candidate: The chosen Spotify candidate (if status is matched).
        score: The match score (if status is matched).
        ranked_alternatives: Ordered list of alternative candidates (if any).
        match_type: The type of match (auto, manual, etc.).
    """

    model_config = {"extra": "forbid"}

    source_item_id: str = Field(description="ID of the source track")
    status: str = Field(description="Match status: matched, unmatched, review")
    selected_candidate: Optional[SpotifyCandidate] = Field(
        default=None,
        description="The chosen Spotify candidate (if status is matched)",
    )
    score: Optional[MatchScore] = Field(
        default=None,
        description="The match score (if status is matched)",
    )
    ranked_alternatives: list[SpotifyCandidate] = Field(
        default_factory=list,
        description="Ordered list of alternative candidates (if any)",
    )
    match_type: Optional[str] = Field(
        default=None,
        description="The type of match: auto, manual, etc.",
    )
    reason: str = Field(
        description="Reason for the match decision",
    )

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Validate that reason is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("Reason cannot be empty")
        return v

    @field_validator("source_item_id")
    @classmethod
    def validate_source_item_id(cls, v: str) -> str:
        """Validate that source_item_id is not empty."""
        if not v or not v.strip():
            raise ValueError("source_item_id cannot be empty")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is a valid value."""
        valid_statuses = {"matched", "unmatched", "review"}
        if v not in valid_statuses:
            raise ValueError(f"status must be one of {valid_statuses}")
        return v

    @field_validator("selected_candidate")
    @classmethod
    def validate_selected_candidate(cls, v: Optional[SpotifyCandidate], info) -> Optional[SpotifyCandidate]:
        """Validate that matched decisions have a selected candidate and unmatched decisions do not."""
        status = info.data.get("status")
        if status == "matched" and v is None:
            raise ValueError("Matched decision must have a selected candidate")
        if status == "unmatched" and v is not None:
            raise ValueError("Unmatched decision must not have a selected candidate")
        return v

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: Optional[MatchScore], info) -> Optional[MatchScore]:
        """Validate that matched decisions have a score and unmatched decisions do not."""
        status = info.data.get("status")
        if status == "matched" and v is None:
            raise ValueError("Matched decision must have a score")
        if status == "unmatched" and v is not None:
            raise ValueError("Unmatched decision must not have a score")
        return v

    @field_validator("ranked_alternatives")
    @classmethod
    def validate_ranked_alternatives(cls, v: list[SpotifyCandidate], info) -> list[SpotifyCandidate]:
        """Validate that ranked_alternatives is a list (always valid)."""
        return v


class TransferRequest(BaseModel):
    """A request to transfer a playlist from a source to a destination.

    Attributes:
        source_url: URL of the source playlist (e.g., YouTube playlist URL).
        source_profile: Profile name for the source service (e.g., YouTube profile).
        spotify_profile: Profile name for the Spotify destination account.
        destination_name: Name to give the destination playlist.
        mode: Transfer mode (dry_run, create, merge, replace).
        match_policy: Policy for accepting matches (strict, balanced, loose).
        public: Whether the destination playlist should be public.

    Example:
        >>> request = TransferRequest(
        ...     source_url="https://www.youtube.com/playlist?list=PL123",
        ...     source_profile="youtube_user",
        ...     spotify_profile="spotify_user",
        ...     destination_name="My Playlist",
        ...     mode=TransferMode.CREATE,
        ...     match_policy=MatchPolicy.BALANCED,
        ...     public=False,
        ... )
        >>> request.source_url
        'https://www.youtube.com/playlist?list=PL123'
    """

    model_config = {"extra": "forbid"}

    source_url: str = Field(description="URL of the source playlist")
    source_profile: str = Field(description="Profile name for the source service")
    spotify_profile: str = Field(description="Profile name for the Spotify destination account")
    destination_name: str = Field(description="Name to give the destination playlist")
    mode: TransferMode = Field(default=TransferMode.DRY_RUN, description="Transfer mode")
    match_policy: MatchPolicy = Field(default=MatchPolicy.BALANCED, description="Policy for accepting matches")
    public: bool = Field(default=False, description="Whether the destination playlist should be public")

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str) -> str:
        """Validate that source_url is not empty."""
        if not v or not v.strip():
            raise ValueError("source_url cannot be empty")
        return v

    @field_validator("source_profile")
    @classmethod
    def validate_source_profile(cls, v: str) -> str:
        """Validate that source_profile is not empty."""
        if not v or not v.strip():
            raise ValueError("source_profile cannot be empty")
        return v

    @field_validator("spotify_profile")
    @classmethod
    def validate_spotify_profile(cls, v: str) -> str:
        """Validate that spotify_profile is not empty."""
        if not v or not v.strip():
            raise ValueError("spotify_profile cannot be empty")
        return v

    @field_validator("destination_name")
    @classmethod
    def validate_destination_name(cls, v: str) -> str:
        """Validate that destination_name is not empty."""
        if not v or not v.strip():
            raise ValueError("destination_name cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_fields(self) -> "TransferRequest":
        """Validate that all required fields are present."""
        # This is a safety net - the field validators above handle empty strings,
        # but we also want to ensure profiles aren't just whitespace.
        if self.source_profile and not self.source_profile.strip():
            raise ValueError("source_profile cannot be whitespace only")
        if self.spotify_profile and not self.spotify_profile.strip():
            raise ValueError("spotify_profile cannot be whitespace only")
        if self.destination_name and not self.destination_name.strip():
            raise ValueError("destination_name cannot be whitespace only")
        return self


class TransferResult(BaseModel):
    """Result of a playlist transfer operation.

    Attributes:
        job_id: Unique identifier for the transfer job.
        status: Current status of the transfer (e.g., "completed", "failed", "cancelled").
        counts: Dictionary of counts for various transfer metrics.
        destination_id: Optional ID of the destination playlist.
        report_paths: List of paths to generated report files.

    Example:
        >>> result = TransferResult(
        ...     job_id="job_123",
        ...     status="completed",
        ...     counts={"total": 50, "matched": 48, "unmatched": 2},
        ...     destination_id="spotify:playlist:abc123",
        ...     report_paths=["reports/job_123.json"],
        ... )
        >>> result.job_id
        'job_123'
    """

    model_config = {"extra": "forbid"}

    job_id: str = Field(description="Unique identifier for the transfer job")
    status: str = Field(description="Current status of the transfer")
    counts: dict[str, int] = Field(description="Counts for various transfer metrics")
    destination_id: Optional[str] = Field(
        default=None,
        description="Optional ID of the destination playlist",
    )
    report_paths: list[str] = Field(
        default_factory=list,
        description="List of paths to generated report files",
    )

    @field_validator("job_id")
    @classmethod
    def validate_job_id(cls, v: str) -> str:
        """Validate that job_id is not empty."""
        if not v or not v.strip():
            raise ValueError("job_id cannot be empty")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is not empty."""
        if not v or not v.strip():
            raise ValueError("status cannot be empty")
        return v


class VerificationResult(BaseModel):
    """Result of verifying destination playlist against expected tracks.

    Attributes:
        is_exact_match: Whether the actual destination matches expected exactly.
        missing_positions: List of expected positions (0-indexed) that are missing.
        extra_positions: List of actual positions (0-indexed) that are extra.
        reordered_positions: List of expected positions that are reordered.
        unavailable_positions: List of expected positions with null/unavailable items.
        expected_items: List of expected track URIs.
        actual_items: List of actual track URIs (may contain None for unavailable).
    """

    is_exact_match: bool = Field(
        description="Whether the actual destination matches expected exactly"
    )
    missing_positions: list[int] = Field(
        default=[],
        description="List of expected positions (0-indexed) that are missing",
    )
    extra_positions: list[int] = Field(
        default=[],
        description="List of actual positions (0-indexed) that are extra",
    )
    reordered_positions: list[int] = Field(
        default=[],
        description="List of expected positions that are reordered",
    )
    unavailable_positions: list[int] = Field(
        default=[],
        description="List of expected positions with null/unavailable items",
    )
    expected_items: list[str] = Field(
        description="List of expected track URIs"
    )
    actual_items: list[str | None] = Field(
        description="List of actual track URIs (may contain None for unavailable)"
    )

    @field_validator("missing_positions", "extra_positions", "reordered_positions", "unavailable_positions")
    @classmethod
    def validate_positions(cls, v: list[int]) -> list[int]:
        """Validate that positions are non-negative."""
        if any(pos < 0 for pos in v):
            raise ValueError("Positions must be non-negative")
        return v

    @field_validator("expected_items")
    @classmethod
    def validate_expected_items(cls, v: list[str]) -> list[str]:
        """Validate expected_items is not empty."""
        if not v:
            raise ValueError("expected_items cannot be empty")
        return v

    @model_validator(mode="after")
    def validate_consistency(self) -> "VerificationResult":
        """Validate that the result is internally consistent."""
        # Check that positions are within bounds
        expected_len = len(self.expected_items)
        actual_len = len(self.actual_items)

        if any(pos >= expected_len for pos in self.missing_positions):
            raise ValueError("missing_positions index out of range")
        if any(pos >= actual_len for pos in self.extra_positions):
            raise ValueError("extra_positions index out of range")
        if any(pos >= expected_len for pos in self.reordered_positions):
            raise ValueError("reordered_positions index out of range")
        if any(pos >= expected_len for pos in self.unavailable_positions):
            raise ValueError("unavailable_positions index out of range")

        # Check that is_exact_match is consistent with empty lists
        if self.is_exact_match:
            if self.missing_positions or self.extra_positions or self.reordered_positions or self.unavailable_positions:
                raise ValueError("is_exact_match True but has mismatch details")
        else:
            if not (self.missing_positions or self.extra_positions or self.reordered_positions or self.unavailable_positions):
                raise ValueError("is_exact_match False but no mismatch details")

        return self


class DestinationPlaylist(BaseModel):
    """A provider-neutral destination playlist model.

    This model represents a playlist in a destination service (e.g., Spotify)
    without exposing provider-specific details or credentials.

    Attributes:
        playlist_id: Unique identifier for the playlist in the provider's system.
        name: Display name of the playlist.
        owner_id: Identifier for the playlist owner.
        public: Whether the playlist is public.
        collaborative: Whether the playlist is collaborative.
        description: Optional description of the playlist.
        snapshot_id: Optional snapshot ID for version tracking.
        external_url: Optional external URL to view the playlist.
        track_count: Number of tracks in the playlist.
    """

    model_config = {"extra": "forbid"}

    playlist_id: str = Field(description="Unique identifier for the playlist")
    name: str = Field(description="Display name of the playlist")
    owner_id: str = Field(description="Identifier for the playlist owner")
    public: bool = Field(description="Whether the playlist is public")
    collaborative: bool = Field(description="Whether the playlist is collaborative")
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the playlist",
    )
    snapshot_id: Optional[str] = Field(
        default=None,
        description="Optional snapshot ID for version tracking",
    )
    external_url: Optional[str] = Field(
        default=None,
        description="Optional external URL to view the playlist",
    )
    track_count: int = Field(
        description="Number of tracks in the playlist",
        ge=0,
    )

    @field_validator("playlist_id")
    @classmethod
    def validate_playlist_id(cls, v: str) -> str:
        """Validate that playlist_id is not empty."""
        if not v or not v.strip():
            raise ValueError("playlist_id cannot be empty")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v

    @field_validator("owner_id")
    @classmethod
    def validate_owner_id(cls, v: str) -> str:
        """Validate that owner_id is not empty."""
        if not v or not v.strip():
            raise ValueError("owner_id cannot be empty")
        return v

    @field_validator("track_count")
    @classmethod
    def validate_track_count(cls, v: int) -> int:
        """Validate that track_count is non-negative."""
        if v < 0:
            raise ValueError("track_count cannot be negative")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourceTrack(BaseModel):
    """A track from a source playlist (e.g., YouTube).

    This model represents a single item in a source playlist, with position
    and metadata, without exposing provider-specific details or credentials.

    Attributes:
        position: Position in the playlist (0-indexed, strictly ascending).
        title: Track title.
        artist_names: List of artist or channel names.
        duration_seconds: Track duration in seconds.
        video_id: Source video ID (e.g., YouTube video ID).
        channel_title: Optional channel title of the uploader.
    """

    model_config = {"extra": "forbid"}

    position: int = Field(description="Position in the playlist (0-indexed)", ge=0)
    title: str = Field(description="Track title")
    artist_names: list[str] = Field(description="List of artist or channel names")
    duration_seconds: int = Field(description="Track duration in seconds", ge=0)
    video_id: str = Field(description="Source video ID")
    channel_title: Optional[str] = Field(
        default=None,
        description="Optional channel title of the uploader",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v

    @field_validator("artist_names")
    @classmethod
    def validate_artist_names(cls, v: list[str]) -> list[str]:
        """Validate that artist_names is not empty."""
        if not v:
            raise ValueError("artist_names cannot be empty")
        return v

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, v: str) -> str:
        """Validate that video_id is not empty."""
        if not v or not v.strip():
            raise ValueError("video_id cannot be empty")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class LoadedSourcePlaylist(BaseModel):
    """A fully loaded source playlist with metadata and ordered tracks.

    This model represents a playlist loaded from a source service (e.g., YouTube)
    with all tracks ordered by position. Tracks must be in strictly ascending
    position order.

    Attributes:
        metadata: Metadata about the playlist.
        tracks: List of tracks in ascending position order.
    """

    model_config = {"extra": "forbid"}

    metadata: SourcePlaylistMetadata = Field(description="Playlist metadata")
    tracks: list[SourceTrack] = Field(description="Tracks in ascending position order")

    @model_validator(mode="after")
    def validate_track_positions(self) -> "LoadedSourcePlaylist":
        """Validate that tracks are in strictly ascending position order."""
        if not self.tracks:
            return self

        positions = [track.position for track in self.tracks]
        # Check for strictly ascending order (no duplicates, no descending)
        for i in range(len(positions) - 1):
            if positions[i] >= positions[i + 1]:
                raise ValueError(
                    f"Tracks must be in strictly ascending position order: "
                    f"position {positions[i]} >= {positions[i + 1]} at index {i}"
                )

        return self

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourcePlaylistMetadata(BaseModel):
    """A provider-neutral source playlist metadata model.

    This model represents metadata for a playlist from a source service (e.g., YouTube)
    without exposing provider-specific details or credentials.

    Attributes:
        reference: Playlist reference (e.g., URL or ID in the source system).
        description: Optional description of the playlist.
        privacy_status: Optional privacy status (e.g., "public", "private", "unlisted").
        owner_channel_id: Optional channel ID of the playlist owner.
        owner_channel_title: Optional channel title of the playlist owner.
        item_count: Number of items in the playlist (non-negative).
    """

    model_config = {"extra": "forbid"}

    reference: str = Field(description="Playlist reference (e.g., URL or ID in the source system)")
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the playlist",
    )
    privacy_status: Optional[str] = Field(
        default=None,
        description="Optional privacy status (e.g., 'public', 'private', 'unlisted')",
    )
    owner_channel_id: Optional[str] = Field(
        default=None,
        description="Optional channel ID of the playlist owner",
    )
    owner_channel_title: Optional[str] = Field(
        default=None,
        description="Optional channel title of the playlist owner",
    )
    item_count: int = Field(
        description="Number of items in the playlist",
        ge=0,
    )

    @field_validator("reference")
    @classmethod
    def validate_reference(cls, v: str) -> str:
        """Validate that reference is not empty."""
        if not v or not v.strip():
            raise ValueError("reference cannot be empty")
        return v

    @field_validator("item_count")
    @classmethod
    def validate_item_count(cls, v: int) -> int:
        """Validate that item_count is non-negative."""
        if v < 0:
            raise ValueError("item_count cannot be negative")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourceTrack(BaseModel):
    """A track from a source playlist (e.g., YouTube).

    This model represents a single item in a source playlist, with position
    and metadata, without exposing provider-specific details or credentials.

    Attributes:
        position: Position in the playlist (0-indexed, strictly ascending).
        title: Track title.
        artist_names: List of artist or channel names.
        duration_seconds: Track duration in seconds.
        video_id: Source video ID (e.g., YouTube video ID).
        channel_title: Optional channel title of the uploader.
    """

    model_config = {"extra": "forbid"}

    position: int = Field(description="Position in the playlist (0-indexed)", ge=0)
    title: str = Field(description="Track title")
    artist_names: list[str] = Field(description="List of artist or channel names")
    duration_seconds: int = Field(description="Track duration in seconds", ge=0)
    video_id: str = Field(description="Source video ID")
    channel_title: Optional[str] = Field(
        default=None,
        description="Optional channel title of the uploader",
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v or not v.strip():
            raise ValueError("title cannot be empty")
        return v

    @field_validator("artist_names")
    @classmethod
    def validate_artist_names(cls, v: list[str]) -> list[str]:
        """Validate that artist_names is not empty."""
        if not v:
            raise ValueError("artist_names cannot be empty")
        return v

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, v: str) -> str:
        """Validate that video_id is not empty."""
        if not v or not v.strip():
            raise ValueError("video_id cannot be empty")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class LoadedSourcePlaylist(BaseModel):
    """A fully loaded source playlist with metadata and ordered tracks.

    This model represents a playlist loaded from a source service (e.g., YouTube)
    with all tracks ordered by position. Tracks must be in strictly ascending
    position order.

    Attributes:
        metadata: Metadata about the playlist.
        tracks: List of tracks in ascending position order.
    """

    model_config = {"extra": "forbid"}

    metadata: SourcePlaylistMetadata = Field(description="Playlist metadata")
    tracks: list[SourceTrack] = Field(description="Tracks in ascending position order")

    @model_validator(mode="after")
    def validate_track_positions(self) -> "LoadedSourcePlaylist":
        """Validate that tracks are in strictly ascending position order."""
        if not self.tracks:
            return self

        positions = [track.position for track in self.tracks]
        # Check for strictly ascending order (no duplicates, no descending)
        for i in range(len(positions) - 1):
            if positions[i] >= positions[i + 1]:
                raise ValueError(
                    f"Tracks must be in strictly ascending position order: "
                    f"position {positions[i]} >= {positions[i + 1]} at index {i}"
                )

        return self

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)
