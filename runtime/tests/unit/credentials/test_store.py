"""Unit tests for credential store operations."""

import pytest

from playlist_bridge.credentials.store import (
    KEYRING_SERVICE_NAME,
    credential_key_name,
)
from playlist_bridge.domain import DestinationService, SourceService


class TestCredentialKeyName:
    """Tests for credential_key_name function."""

    def test_same_inputs_return_same_key(self) -> None:
        """The same inputs should return the same key."""
        service = SourceService.YOUTUBE
        profile = "test_profile"

        key1 = credential_key_name(service, profile)
        key2 = credential_key_name(service, profile)

        assert key1 == key2

    def test_distinct_services_return_distinct_keys(self) -> None:
        """Different services should return different keys."""
        profile = "test_profile"

        youtube_key = credential_key_name(SourceService.YOUTUBE, profile)
        spotify_key = credential_key_name(DestinationService.SPOTIFY, profile)

        assert youtube_key != spotify_key

    def test_distinct_profiles_return_distinct_keys(self) -> None:
        """Different profile names should return different keys."""
        service = SourceService.YOUTUBE

        key1 = credential_key_name(service, "profile1")
        key2 = credential_key_name(service, "profile2")

        assert key1 != key2

    def test_key_starts_with_service_name(self) -> None:
        """The key should start with the fixed service name."""
        key = credential_key_name(SourceService.YOUTUBE, "test")
        assert key.startswith(KEYRING_SERVICE_NAME)

    def test_key_contains_service_value(self) -> None:
        """The key should contain the service value."""
        key = credential_key_name(SourceService.YOUTUBE, "test")
        assert "youtube" in key

        key = credential_key_name(DestinationService.SPOTIFY, "test")
        assert "spotify" in key

    def test_raises_value_error_for_none_service(self) -> None:
        """Passing None as service should raise ValueError."""
        with pytest.raises(ValueError, match="service must not be None"):
            credential_key_name(None, "test")  # type: ignore[arg-type]

    def test_raises_value_error_for_empty_profile_name(self) -> None:
        """Passing empty string as profile_name should raise ValueError."""
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            credential_key_name(SourceService.YOUTUBE, "")

    def test_raises_value_error_for_none_profile_name(self) -> None:
        """Passing None as profile_name should raise ValueError."""
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            credential_key_name(SourceService.YOUTUBE, None)  # type: ignore[arg-type]
