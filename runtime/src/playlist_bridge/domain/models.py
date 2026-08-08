"""Domain models for the playlist bridge."""

from typing import Optional, Literal

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


class AccountProfile(BaseModel):
    """Account profile for a user on a provider.

    Attributes:
        provider: Service provider (e.g., "spotify", "youtube").
        account_id: Provider-specific account ID.
        display_name: Human-readable display name.
        email: Optional email address.
        username: Optional username.
        profile_url: Optional URL to the user's profile.
    """

    model_config = {"extra": "forbid"}

    provider: str = Field(description="Service provider")
    account_id: str = Field(description="Provider-specific account ID")
    display_name: str = Field(description="Human-readable display name")
    email: Optional[str] = Field(default=None, description="Optional email address")
    username: Optional[str] = Field(default=None, description="Optional username")
    profile_url: Optional[str] = Field(default=None, description="Optional URL to profile")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate that provider is not empty."""
        if not v or not v.strip():
            raise ValueError("provider cannot be empty")
        return v

    @field_validator("account_id")
    @classmethod
    def validate_account_id(cls, v: str) -> str:
        """Validate that account_id is not empty."""
        if not v or not v.strip():
            raise ValueError("account_id cannot be empty")
        return v

    @field_validator("display_name")
    @classmethod
    def validate_display_name(cls, v: str) -> str:
        """Validate that display_name is not empty."""
        if not v or not v.strip():
            raise ValueError("display_name cannot be empty")
        return v


class PlaylistReference(BaseModel):
    """Reference to a playlist on a provider.

    Attributes:
        provider: Service provider (e.g., "spotify", "youtube").
        playlist_id: Provider-specific playlist ID.
        name: Playlist name.
        owner: Owner identifier or display name.
    """

    model_config = {"extra": "forbid"}

    provider: str = Field(description="Service provider")
    playlist_id: str = Field(description="Provider-specific playlist ID")
    name: str = Field(description="Playlist name")
    owner: str = Field(description="Owner identifier or display name")

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate that provider is not empty."""
        if not v or not v.strip():
            raise ValueError("provider cannot be empty")
        return v

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

    @field_validator("owner")
    @classmethod
    def validate_owner(cls, v: str) -> str:
        """Validate that owner is not empty."""
        if not v or not v.strip():
            raise ValueError("owner cannot be empty")
        return v


class TransferRequest(BaseModel):
    """Request to transfer a playlist from source to destination.

    Attributes:
        source_service: Source service (e.g., "youtube").
        source_playlist_id: Playlist ID on the source service.
        destination_service: Destination service (e.g., "spotify").
        destination_playlist_id: Playlist ID on the destination service.
        destination_name: Destination playlist name (for create mode).
        transfer_mode: Mode of transfer (dry_run, create, merge, replace).
        match_policy: Match policy (strict, balanced, loose).
        visibility: Whether the destination playlist should be public or private.
        dry_run: If True, simulate without writing changes.
        job_id: Optional job ID for resuming.
    """

    model_config = {"extra": "forbid"}

    source_service: str = Field(description="Source service")
    source_playlist_id: str = Field(description="Playlist ID on source service")
    destination_service: str = Field(description="Destination service")
    destination_playlist_id: Optional[str] = Field(
        default=None,
        description="Playlist ID on destination service (for merge/replace)",
    )
    destination_name: Optional[str] = Field(
        default=None,
        description="Destination playlist name (for create mode)",
    )
    transfer_mode: TransferMode = Field(default=TransferMode.DRY_RUN, description="Transfer mode")
    match_policy: MatchPolicy = Field(default=MatchPolicy.BALANCED, description="Match policy")
    visibility: Optional[str] = Field(default="private", description="Playlist visibility")
    dry_run: bool = Field(default=False, description="If True, simulate without writing")
    job_id: Optional[str] = Field(default=None, description="Optional job ID for resuming")

    @model_validator(mode="after")
    def validate_destination_fields(self) -> "TransferRequest":
        """Validate that destination fields are appropriate for the transfer mode."""
        if self.transfer_mode == TransferMode.CREATE:
            if not self.destination_name:
                raise ValueError("destination_name is required for CREATE mode")
        elif self.transfer_mode in (TransferMode.MERGE, TransferMode.REPLACE):
            if not self.destination_playlist_id:
                raise ValueError("destination_playlist_id is required for MERGE/REPLACE modes")
        return self


class MatchDecision(BaseModel):
    """Decision for matching a source track to a destination track.

    Attributes:
        source_item_id: Identifier for the source item.
        destination_uri: Destination track URI (e.g., spotify:track:...).
        destination_track_id: Destination track ID.
        destination_title: Destination track title.
        destination_artist_names: Destination artist names.
        score: Match score (0.0 to 1.0).
        decision_type: Type of decision (accepted, review, rejected, etc.).
        confidence: Confidence level (0.0 to 1.0).
    """

    model_config = {"extra": "forbid"}

    source_item_id: str = Field(description="Identifier for the source item")
    destination_uri: str = Field(description="Destination track URI")
    destination_track_id: str = Field(description="Destination track ID")
    destination_title: str = Field(description="Destination track title")
    destination_artist_names: list[str] = Field(description="Destination artist names")
    score: float = Field(description="Match score", ge=0.0, le=1.0)
    decision_type: str = Field(description="Type of decision")
    confidence: float = Field(description="Confidence level", ge=0.0, le=1.0)

    @field_validator("source_item_id")
    @classmethod
    def validate_source_item_id(cls, v: str) -> str:
        """Validate that source_item_id is not empty."""
        if not v or not v.strip():
            raise ValueError("source_item_id cannot be empty")
        return v

    @field_validator("destination_uri")
    @classmethod
    def validate_destination_uri(cls, v: str) -> str:
        """Validate that destination_uri is not empty."""
        if not v or not v.strip():
            raise ValueError("destination_uri cannot be empty")
        return v

    @field_validator("destination_track_id")
    @classmethod
    def validate_destination_track_id(cls, v: str) -> str:
        """Validate that destination_track_id is not empty."""
        if not v or not v.strip():
            raise ValueError("destination_track_id cannot be empty")
        return v

    @field_validator("destination_title")
    @classmethod
    def validate_destination_title(cls, v: str) -> str:
        """Validate that destination_title is not empty."""
        if not v or not v.strip():
            raise ValueError("destination_title cannot be empty")
        return v

    @field_validator("destination_artist_names")
    @classmethod
    def validate_destination_artist_names(cls, v: list[str]) -> list[str]:
        """Validate that destination_artist_names is not empty."""
        if not v:
            raise ValueError("destination_artist_names cannot be empty")
        return v


class MatchScore(BaseModel):
    """Score for a match between a source and destination track.

    Attributes:
        source_item_id: Identifier for the source item.
        destination_uri: Destination track URI.
        score: Match score (0.0 to 1.0).
        title_similarity: Similarity score for title (0.0 to 1.0).
        artist_similarity: Similarity score for artists (0.0 to 1.0).
        duration_similarity: Similarity score for duration (0.0 to 1.0).
        version_agreement: Agreement score for version tokens (0.0 to 1.0).
        explicit_agreement: Agreement score for explicit state (0.0 to 1.0).
        total_score: Aggregated total score (0.0 to 1.0).
    """

    model_config = {"extra": "forbid"}

    source_item_id: str = Field(description="Identifier for the source item")
    destination_uri: str = Field(description="Destination track URI")
    score: float = Field(description="Match score", ge=0.0, le=1.0)
    title_similarity: float = Field(description="Title similarity", ge=0.0, le=1.0)
    artist_similarity: float = Field(description="Artist similarity", ge=0.0, le=1.0)
    duration_similarity: float = Field(description="Duration similarity", ge=0.0, le=1.0)
    version_agreement: float = Field(description="Version agreement", ge=0.0, le=1.0)
    explicit_agreement: float = Field(description="Explicit agreement", ge=0.0, le=1.0)
    total_score: float = Field(description="Aggregated total score", ge=0.0, le=1.0)


class NormalizedTrackHint(BaseModel):
    """Normalized hint for matching source tracks.

    Attributes:
        source_item_id: Identifier for the source item.
        normalized_title: Normalized title text.
        normalized_artist: Normalized artist text.
        classification: Classification of the source item.
        version_tokens: Version tokens extracted from the title.
        unwanted_flags: Unwanted flags detected.
        artist_hints: Artist hints for matching.
    """

    model_config = {"extra": "forbid"}

    source_item_id: str = Field(description="Identifier for the source item")
    normalized_title: str = Field(description="Normalized title text")
    normalized_artist: str = Field(description="Normalized artist text")
    classification: str = Field(description="Classification of the source item")
    version_tokens: tuple[str, ...] = Field(description="Version tokens extracted from title")
    unwanted_flags: tuple[str, ...] = Field(description="Unwanted flags detected")
    artist_hints: tuple[str, ...] = Field(description="Artist hints for matching")

    @field_validator("source_item_id")
    @classmethod
    def validate_source_item_id(cls, v: str) -> str:
        """Validate that source_item_id is not empty."""
        if not v or not v.strip():
            raise ValueError("source_item_id cannot be empty")
        return v

    @field_validator("normalized_title")
    @classmethod
    def validate_normalized_title(cls, v: str) -> str:
        """Validate that normalized_title is not empty."""
        if not v or not v.strip():
            raise ValueError("normalized_title cannot be empty")
        return v

    @field_validator("classification")
    @classmethod
    def validate_classification(cls, v: str) -> str:
        """Validate that classification is not empty."""
        if not v or not v.strip():
            raise ValueError("classification cannot be empty")
        return v

    @field_validator("version_tokens")
    @classmethod
    def validate_version_tokens(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        """Validate that version_tokens are sorted and unique."""
        if not all(isinstance(t, str) for t in v):
            raise ValueError("version_tokens must contain only strings")
        # Check that all tokens are lowercase
        if any(t != t.lower() for t in v):
            raise ValueError("version_tokens must be lowercase")
        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("version_tokens must be unique")
        # Check sorted order
        if list(v) != sorted(v):
            raise ValueError("version_tokens must be sorted")
        return v

    @field_validator("unwanted_flags")
    @classmethod
    def validate_unwanted_flags(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        """Validate that unwanted_flags are sorted and unique."""
        if not all(isinstance(f, str) for f in v):
            raise ValueError("unwanted_flags must contain only strings")
        # Check that all flags are lowercase
        if any(f != f.lower() for f in v):
            raise ValueError("unwanted_flags must be lowercase")
        # Check for duplicates
        if len(set(v)) != len(v):
            raise ValueError("unwanted_flags must be unique")
        # Check sorted order
        if list(v) != sorted(v):
            raise ValueError("unwanted_flags must be sorted")
        return v

    @field_validator("artist_hints")
    @classmethod
    def validate_artist_hints(cls, v: tuple[str, ...]) -> tuple[str, ...]:
        """Validate that artist_hints is not empty and tuple elements are strings."""
        if not v:
            raise ValueError("artist_hints cannot be empty")
        if not all(isinstance(a, str) for a in v):
            raise ValueError("artist_hints must contain only strings")
        return v

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to ensure consistent serialization."""
        return super().model_dump(**kwargs)


class SourcePlaylistMetadata(BaseModel):
    """Metadata for a source playlist.

    Attributes:
        reference: Reference to the playlist.
        description: Playlist description.
        privacy_status: Privacy status (public, private, unlisted).
        owner_channel_id: Channel ID of the owner.
        owner_channel_title: Channel title of the owner.
        item_count: Number of items in the playlist.
    """

    model_config = {"extra": "forbid"}

    reference: PlaylistReference = Field(description="Playlist reference")
    description: str = Field(default="", description="Playlist description")
    privacy_status: str = Field(default="private", description="Privacy status")
    owner_channel_id: str = Field(description="Channel ID of the owner")
    owner_channel_title: str = Field(description="Channel title of the owner")
    item_count: int = Field(description="Number of items in the playlist", ge=0)


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


class ItemPage(BaseModel):
    """A page of items from a source playlist.

    This model represents a single page of items retrieved from a source
    service (e.g., YouTube) with pagination support.

    Attributes:
        items: List of source tracks in this page.
        next_page_token: Token to retrieve the next page, or None if this is the last page.
        total_count: Optional total number of items in the playlist.
        has_more: Whether there are more pages available.
    """

    model_config = {"extra": "forbid"}

    items: list[SourceTrack] = Field(description="Source tracks in this page")
    next_page_token: Optional[str] = Field(
        default=None,
        description="Token to retrieve the next page, or None if last page",
    )
    total_count: Optional[int] = Field(
        default=None,
        description="Optional total number of items in the playlist",
        ge=0,
    )
    has_more: bool = Field(description="Whether there are more pages available")


class PolicyThresholds(BaseModel):
    """Policy-specific thresholds for match acceptance decisions.

    Attributes:
        auto_accept_score: Minimum score to automatically accept a match without review.
        minimum_runner_up_gap: Minimum score gap between top and second-best candidate.
        review_floor: Minimum score required for a match to be considered for review.
    """

    model_config = {"extra": "forbid"}

    auto_accept_score: float = Field(
        description="Minimum score to automatically accept a match without review",
        ge=0.0,
        le=1.0,
    )
    minimum_runner_up_gap: float = Field(
        description="Minimum score gap between top and second-best candidate",
        ge=0.0,
        le=1.0,
    )
    review_floor: float = Field(
        description="Minimum score required for a match to be considered for review",
        ge=0.0,
        le=1.0,
    )

    @model_validator(mode="after")
    def validate_threshold_consistency(self) -> "PolicyThresholds":
        """Validate that thresholds are logically consistent."""
        if self.review_floor > self.auto_accept_score:
            raise ValueError(
                f"review_floor ({self.review_floor}) cannot exceed "
                f"auto_accept_score ({self.auto_accept_score})"
            )
        return self


class MatchingConfig(BaseModel):
    """Configuration for the matching engine.

    Attributes:
        schema_version: Version of the configuration schema.
        title_weight: Weight for title similarity scoring.
        artist_weight: Weight for artist similarity scoring.
        duration_weight: Weight for duration similarity scoring.
        version_weight: Weight for version token agreement scoring.
        explicit_weight: Weight for explicit state matching.
        unwanted_version_penalty: Penalty for unwanted version indicators.
        version_contradiction_penalty: Penalty for version token contradictions.
        explicit_mismatch_penalty: Penalty for explicit state mismatch.
        duration_full_credit_floor_ms: Minimum duration difference in ms for full credit.
        duration_full_credit_ratio: Ratio threshold for full duration credit.
        duration_zero_credit_floor_ms: Duration difference in ms for zero credit.
        duration_zero_credit_ratio: Ratio threshold for zero duration credit.
        max_queries_per_track: Maximum number of search queries per track.
        results_per_query: Number of results to fetch per search query.
        max_unique_candidates: Maximum unique candidates to consider per track.
        cache_freshness_days: Number of days before cached matches expire.
        policy_thresholds: Thresholds for each MatchPolicy variant.
    """

    model_config = {"extra": "forbid"}

    schema_version: Literal[1] = Field(description="Version of the configuration schema")
    title_weight: float = Field(description="Weight for title similarity scoring", ge=0.0, le=1.0)
    artist_weight: float = Field(description="Weight for artist similarity scoring", ge=0.0, le=1.0)
    duration_weight: float = Field(description="Weight for duration similarity scoring", ge=0.0, le=1.0)
    version_weight: float = Field(description="Weight for version token agreement scoring", ge=0.0, le=1.0)
    explicit_weight: float = Field(description="Weight for explicit state matching", ge=0.0, le=1.0)
    unwanted_version_penalty: float = Field(
        description="Penalty for unwanted version indicators",
        ge=0.0,
        le=1.0,
    )
    version_contradiction_penalty: float = Field(
        description="Penalty for version token contradictions",
        ge=0.0,
        le=1.0,
    )
    explicit_mismatch_penalty: float = Field(
        description="Penalty for explicit state mismatch",
        ge=0.0,
        le=1.0,
    )
    duration_full_credit_floor_ms: int = Field(
        description="Minimum duration difference in ms for full credit",
        ge=0,
    )
    duration_full_credit_ratio: float = Field(
        description="Ratio threshold for full duration credit",
        ge=0.0,
        le=1.0,
    )
    duration_zero_credit_floor_ms: int = Field(
        description="Duration difference in ms for zero credit",
        ge=0,
    )
    duration_zero_credit_ratio: float = Field(
        description="Ratio threshold for zero duration credit",
        ge=0.0,
        le=1.0,
    )
    max_queries_per_track: int = Field(
        description="Maximum number of search queries per track",
        ge=1,
    )
    results_per_query: int = Field(
        description="Number of results to fetch per search query",
        ge=1,
    )
    max_unique_candidates: int = Field(
        description="Maximum unique candidates to consider per track",
        ge=1,
    )
    cache_freshness_days: int = Field(
        description="Number of days before cached matches expire",
        ge=0,
    )
    policy_thresholds: dict[MatchPolicy, PolicyThresholds] = Field(
        description="Thresholds for each MatchPolicy variant"
    )

    @model_validator(mode="after")
    def validate_policy_thresholds_complete(self) -> "MatchingConfig":
        """Validate that thresholds exist for all MatchPolicy variants."""
        required_policies = set(MatchPolicy)
        provided_policies = set(self.policy_thresholds.keys())
        missing = required_policies - provided_policies
        if missing:
            raise ValueError(
                f"Missing policy thresholds for: {', '.join(p.value for p in missing)}"
            )
        return self