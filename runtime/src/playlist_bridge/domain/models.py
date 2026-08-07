"""Domain models for the playlist bridge."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


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
