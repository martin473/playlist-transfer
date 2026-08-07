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

    @field_validator("reasons")
    @classmethod
    def validate_reasons(cls, v: list[str]) -> list[str]:
        """Validate that reasons are non-empty strings."""
        for reason in v:
            if not reason.strip():
                raise ValueError("Reason strings cannot be empty or whitespace only")
        return v


class MatchDecision(BaseModel):
    """A decision about whether a source track matches a Spotify candidate.

    Attributes:
        source_item_id: The ID of the source item being matched.
        status: The status of the match ("matched" or "unmatched").
        selected_candidate: The selected Spotify candidate, if matched.
        ranked_alternatives: Ranked list of alternative candidates.
        score: The score of the selected candidate, if matched.
        reason: A reason for the decision.
    """

    source_item_id: str = Field(description="The ID of the source item being matched")
    status: str = Field(description='The status of the match ("matched" or "unmatched")')
    selected_candidate: Optional[SpotifyCandidate] = Field(
        default=None,
        description="The selected Spotify candidate, if matched",
    )
    ranked_alternatives: list[SpotifyCandidate] = Field(
        default_factory=list,
        description="Ranked list of alternative candidates",
    )
    score: Optional[MatchScore] = Field(
        default=None,
        description="The score of the selected candidate, if matched",
    )
    reason: str = Field(
        description="A reason for the decision",
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that the status is either 'matched' or 'unmatched'."""
        allowed = {"matched", "unmatched"}
        if v not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return v

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v: str) -> str:
        """Validate that the reason is not empty."""
        if not v.strip():
            raise ValueError("Reason cannot be empty")
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
