"""Unit tests for credential and profile ports."""

import pytest
from typing import Any, Mapping

from playlist_bridge.domain.enums import DestinationService, SourceService
from playlist_bridge.ports import (
    CredentialCorruptionError,
    CredentialStore,
    AccountProfileRepository,
    IntegrityError,
    KeyringError,
)


# ============================================================================
# Fake implementations for testing the protocols
# ============================================================================


class InMemoryCredentialStore:
    """In-memory fake implementation of CredentialStore for testing."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], dict[str, Any]] = {}

    def save(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
        token_payload: Mapping[str, Any],
    ) -> None:
        """Save credentials to the in-memory store."""
        # Validate serializability
        if not isinstance(token_payload, dict):
            raise CredentialCorruptionError(
                service=str(service),
                profile_name=profile_name,
                safe_message="token_payload must be a dict",
            )
        # Convert to dict for storage
        self._store[(str(service), profile_name)] = dict(token_payload)

    def load(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
    ) -> dict[str, Any] | None:
        """Load credentials from the in-memory store."""
        key = (str(service), profile_name)
        if key not in self._store:
            return None
        # Simulate corruption check
        data = self._store[key]
        if not isinstance(data, dict):
            raise CredentialCorruptionError(
                service=str(service),
                profile_name=profile_name,
                safe_message="stored data is not a dict",
            )
        return dict(data)

    def delete(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
    ) -> bool:
        """Delete credentials from the in-memory store."""
        key = (str(service), profile_name)
        if key not in self._store:
            return False
        del self._store[key]
        return True


class FakeAccountProfile:
    """Fake AccountProfile for testing the repository protocol."""

    def __init__(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
        account_id: str,
        display_name: str,
    ) -> None:
        self.service = service
        self.profile_name = profile_name
        self.account_id = account_id
        self.display_name = display_name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FakeAccountProfile):
            return False
        return (
            self.service == other.service
            and self.profile_name == other.profile_name
            and self.account_id == other.account_id
            and self.display_name == other.display_name
        )

    def __repr__(self) -> str:
        return (
            f"FakeAccountProfile(service={self.service!r}, "
            f"profile_name={self.profile_name!r}, "
            f"account_id={self.account_id!r}, "
            f"display_name={self.display_name!r})"
        )


class InMemoryAccountProfileRepository:
    """In-memory fake implementation of AccountProfileRepository for testing."""

    def __init__(self) -> None:
        self._profiles: dict[tuple[str, str], FakeAccountProfile] = {}

    def save(self, profile: FakeAccountProfile) -> FakeAccountProfile:
        """Save a profile to the in-memory repository."""
        key = (str(profile.service), profile.profile_name)
        if key in self._profiles:
            # Simulate integrity error on duplicate
            raise IntegrityError(
                f"Profile {profile.profile_name} for {profile.service} already exists"
            )
        self._profiles[key] = profile
        return profile

    def get(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
    ) -> FakeAccountProfile | None:
        """Get a profile by service and profile name."""
        key = (str(service), profile_name)
        return self._profiles.get(key)

    def list(
        self,
        service: SourceService | DestinationService | None = None,
    ) -> list[FakeAccountProfile]:
        """List profiles, optionally filtered by service."""
        if service is None:
            return list(self._profiles.values())
        return [
            p
            for (svc, _), p in self._profiles.items()
            if svc == str(service)
        ]


# ============================================================================
# Tests for CredentialStore protocol
# ============================================================================


class TestCredentialStore:
    """Test that CredentialStore protocol is satisfied by fake implementation."""

    def test_fake_store_satisfies_protocol(self) -> None:
        """Verify that InMemoryCredentialStore satisfies the CredentialStore protocol."""
        store: CredentialStore = InMemoryCredentialStore()
        assert isinstance(store, CredentialStore)

    def test_save_and_load_round_trip(self) -> None:
        """Test save and load round trip with valid data."""
        store = InMemoryCredentialStore()
        service = SourceService.YOUTUBE
        profile_name = "default"
        token_payload = {"access_token": "token123", "refresh_token": "refresh456"}

        store.save(service, profile_name, token_payload)
        loaded = store.load(service, profile_name)

        assert loaded is not None
        assert loaded["access_token"] == "token123"
        assert loaded["refresh_token"] == "refresh456"

    def test_load_missing_returns_none(self) -> None:
        """Test load returns None for non-existent credentials."""
        store = InMemoryCredentialStore()
        result = store.load(SourceService.YOUTUBE, "nonexistent")
        assert result is None

    def test_delete_returns_true_when_exists(self) -> None:
        """Test delete returns True when credentials existed."""
        store = InMemoryCredentialStore()
        service = SourceService.YOUTUBE
        profile_name = "default"
        store.save(service, profile_name, {"token": "value"})

        deleted = store.delete(service, profile_name)
        assert deleted is True
        assert store.load(service, profile_name) is None

    def test_delete_returns_false_when_missing(self) -> None:
        """Test delete returns False when credentials did not exist."""
        store = InMemoryCredentialStore()
        deleted = store.delete(SourceService.YOUTUBE, "nonexistent")
        assert deleted is False

    def test_save_raises_credential_corruption_error(self) -> None:
        """Test save raises CredentialCorruptionError for invalid payload."""
        store = InMemoryCredentialStore()

        # The fake store only validates that token_payload is a dict
        # We need to force an error by passing something that raises
        with pytest.raises(CredentialCorruptionError) as exc:
            # Pass a non-dict to trigger the validation
            store.save(
                SourceService.YOUTUBE,
                "default",
                "not_a_dict",  # type: ignore[arg-type]
            )
        assert "token_payload must be a dict" in str(exc.value)
        assert exc.value.service == "SourceService.YOUTUBE"
        assert exc.value.profile_name == "default"

    def test_load_raises_credential_corruption_error(self) -> None:
        """Test load raises CredentialCorruptionError for corrupted data."""
        store = InMemoryCredentialStore()
        service = SourceService.YOUTUBE
        profile_name = "default"

        # Manually corrupt the store
        store._store[(str(service), profile_name)] = "corrupted"  # type: ignore[assignment]

        with pytest.raises(CredentialCorruptionError) as exc:
            store.load(service, profile_name)
        assert "stored data is not a dict" in str(exc.value)
        assert exc.value.service == "SourceService.YOUTUBE"
        assert exc.value.profile_name == "default"


# ============================================================================
# Tests for AccountProfileRepository protocol
# ============================================================================


class TestAccountProfileRepository:
    """Test that AccountProfileRepository protocol is satisfied by fake implementation."""

    def test_fake_repository_satisfies_protocol(self) -> None:
        """Verify that InMemoryAccountProfileRepository satisfies the protocol."""
        repo: AccountProfileRepository = InMemoryAccountProfileRepository()
        assert isinstance(repo, AccountProfileRepository)

    def test_save_and_get_round_trip(self) -> None:
        """Test save and get round trip with valid data."""
        repo = InMemoryAccountProfileRepository()
        profile = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )

        saved = repo.save(profile)
        loaded = repo.get(SourceService.YOUTUBE, "default")

        assert loaded is not None
        assert loaded == saved
        assert loaded.profile_name == "default"
        assert loaded.account_id == "channel123"
        assert loaded.display_name == "My YouTube Channel"

    def test_get_missing_returns_none(self) -> None:
        """Test get returns None for non-existent profile."""
        repo = InMemoryAccountProfileRepository()
        result = repo.get(SourceService.YOUTUBE, "nonexistent")
        assert result is None

    def test_save_raises_integrity_error_on_duplicate(self) -> None:
        """Test save raises IntegrityError for duplicate profiles."""
        repo = InMemoryAccountProfileRepository()
        profile = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )

        repo.save(profile)

        duplicate = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel456",
            display_name="Another Channel",
        )

        with pytest.raises(IntegrityError) as exc:
            repo.save(duplicate)
        assert "already exists" in str(exc.value)

    def test_list_all_profiles(self) -> None:
        """Test list returns all profiles when no service filter provided."""
        repo = InMemoryAccountProfileRepository()

        profile1 = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )
        profile2 = FakeAccountProfile(
            service=DestinationService.SPOTIFY,
            profile_name="work",
            account_id="user456",
            display_name="Work Spotify",
        )

        repo.save(profile1)
        repo.save(profile2)

        all_profiles = repo.list()
        assert len(all_profiles) == 2
        assert profile1 in all_profiles
        assert profile2 in all_profiles

    def test_list_filters_by_service(self) -> None:
        """Test list filters profiles by service."""
        repo = InMemoryAccountProfileRepository()

        profile1 = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )
        profile2 = FakeAccountProfile(
            service=DestinationService.SPOTIFY,
            profile_name="work",
            account_id="user456",
            display_name="Work Spotify",
        )

        repo.save(profile1)
        repo.save(profile2)

        youtube_profiles = repo.list(service=SourceService.YOUTUBE)
        assert len(youtube_profiles) == 1
        assert youtube_profiles[0] == profile1

        spotify_profiles = repo.list(service=DestinationService.SPOTIFY)
        assert len(spotify_profiles) == 1
        assert spotify_profiles[0] == profile2

    def test_list_returns_empty_when_none(self) -> None:
        """Test list returns empty list when no profiles match."""
        repo = InMemoryAccountProfileRepository()
        result = repo.list(service=SourceService.YOUTUBE)
        assert result == []


# ============================================================================
# Tests for error types
# ============================================================================


class TestErrorTypes:
    """Test that custom error types are properly defined."""

    def test_credential_corruption_error(self) -> None:
        """Test CredentialCorruptionError initialization."""
        err = CredentialCorruptionError(
            service="spotify",
            profile_name="default",
            safe_message="Token payload malformed",
        )
        assert err.service == "spotify"
        assert err.profile_name == "default"
        assert err.safe_message == "Token payload malformed"
        assert "spotify/default" in str(err)
        assert "Token payload malformed" in str(err)

    def test_keyring_error(self) -> None:
        """Test KeyringError initialization."""
        err = KeyringError("Keychain unlock failed")
        assert str(err) == "Keychain unlock failed"

    def test_integrity_error(self) -> None:
        """Test IntegrityError initialization."""
        err = IntegrityError("UNIQUE constraint failed")
        assert str(err) == "UNIQUE constraint failed"
