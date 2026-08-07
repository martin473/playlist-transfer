"""Unit tests for credential store operations."""

import json

import pytest

from playlist_bridge.credentials.store import (
    KEYRING_SERVICE_NAME,
    credential_key_name,
    delete_token,
    load_token,
    save_token,
)
from playlist_bridge.domain import DestinationService, SourceService
from playlist_bridge.ports import CredentialCorruptionError, KeyringError


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
            credential_key_name(None, "test")

    def test_raises_value_error_for_empty_profile_name(self) -> None:
        """Passing empty string as profile_name should raise ValueError."""
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            credential_key_name(SourceService.YOUTUBE, "")

    def test_raises_value_error_for_none_profile_name(self) -> None:
        """Passing None as profile_name should raise ValueError."""
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            credential_key_name(SourceService.YOUTUBE, None)


class TestSaveToken:
    """Tests for save_token function."""

    def test_save_token_stores_serialized_payload(self) -> None:
        """save_token should store the token as JSON in the keyring backend."""
        backend = InMemoryKeyringBackend()
        service = SourceService.YOUTUBE
        profile = "test_profile"
        token_payload = {"access_token": "abc123", "refresh_token": "def456"}

        save_token(backend, service, profile, token_payload)

        key = credential_key_name(service, profile)
        stored = backend.get_password(KEYRING_SERVICE_NAME, key)
        assert stored is not None
        assert json.loads(stored) == token_payload

    def test_save_token_raises_value_error_for_none_service(self) -> None:
        """save_token should raise ValueError if service is None."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="service must not be None"):
            save_token(backend, None, "profile", {})

    def test_save_token_raises_value_error_for_empty_profile(self) -> None:
        """save_token should raise ValueError if profile_name is empty."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            save_token(backend, SourceService.YOUTUBE, "", {})

    def test_save_token_raises_value_error_for_none_payload(self) -> None:
        """save_token should raise ValueError if token_payload is None."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="token_payload must not be None"):
            save_token(backend, SourceService.YOUTUBE, "profile", None)

    def test_save_token_raises_value_error_for_non_serializable_payload(self) -> None:
        """save_token should raise ValueError if token_payload is not JSON-serializable."""
        backend = InMemoryKeyringBackend()

        class NonSerializable:
            pass

        with pytest.raises(ValueError, match="Token payload is not JSON-serializable"):
            save_token(backend, SourceService.YOUTUBE, "profile", {"bad": NonSerializable()})

    def test_save_token_raises_keyring_error_on_backend_failure(self) -> None:
        """save_token should raise KeyringError when the keyring backend fails."""
        backend = FailingKeyringBackend()

        with pytest.raises(KeyringError, match="Failed to save token"):
            save_token(backend, SourceService.YOUTUBE, "profile", {"token": "value"})


class TestLoadToken:
    """Tests for load_token function."""

    def test_load_token_returns_stored_payload(self) -> None:
        """load_token should retrieve and deserialize the stored token."""
        backend = InMemoryKeyringBackend()
        service = DestinationService.SPOTIFY
        profile = "spotify_user"
        token_payload = {"access_token": "xyz789", "expires_in": 3600}

        save_token(backend, service, profile, token_payload)
        loaded = load_token(backend, service, profile)

        assert loaded == token_payload

    def test_load_token_returns_empty_dict_for_missing_token(self) -> None:
        """load_token should return an empty dict when no token is stored."""
        backend = InMemoryKeyringBackend()

        loaded = load_token(backend, SourceService.YOUTUBE, "nonexistent")

        assert loaded == {}

    def test_load_token_raises_value_error_for_none_service(self) -> None:
        """load_token should raise ValueError if service is None."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="service must not be None"):
            load_token(backend, None, "profile")

    def test_load_token_raises_value_error_for_empty_profile(self) -> None:
        """load_token should raise ValueError if profile_name is empty."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            load_token(backend, SourceService.YOUTUBE, "")

    def test_load_token_raises_credential_corruption_for_invalid_json(self) -> None:
        """load_token should raise CredentialCorruptionError for invalid JSON."""
        backend = InMemoryKeyringBackend()
        service = SourceService.YOUTUBE
        profile = "corrupted"
        key = credential_key_name(service, profile)

        # Store invalid JSON directly
        backend.set_password(KEYRING_SERVICE_NAME, key, "not valid json")

        with pytest.raises(CredentialCorruptionError, match="Stored payload is not valid JSON"):
            load_token(backend, service, profile)

    def test_load_token_raises_credential_corruption_for_non_dict_payload(self) -> None:
        """load_token should raise CredentialCorruptionError for non-dict JSON."""
        backend = InMemoryKeyringBackend()
        service = SourceService.YOUTUBE
        profile = "corrupted"
        key = credential_key_name(service, profile)

        # Store a JSON array instead of an object
        backend.set_password(KEYRING_SERVICE_NAME, key, json.dumps(["not", "a", "dict"]))

        with pytest.raises(CredentialCorruptionError, match="Stored payload is not a JSON object"):
            load_token(backend, service, profile)

    def test_load_token_raises_keyring_error_on_backend_failure(self) -> None:
        """load_token should raise KeyringError when the keyring backend fails."""
        backend = FailingKeyringBackend()

        with pytest.raises(KeyringError, match="Failed to load token"):
            load_token(backend, SourceService.YOUTUBE, "profile")


class TestDeleteToken:
    """Tests for delete_token function."""

    def test_delete_token_removes_stored_token(self) -> None:
        """delete_token should remove the token from the keyring."""
        backend = InMemoryKeyringBackend()
        service = SourceService.YOUTUBE
        profile = "test_profile"
        token_payload = {"token": "value"}

        save_token(backend, service, profile, token_payload)
        delete_token(backend, service, profile)

        key = credential_key_name(service, profile)
        stored = backend.get_password(KEYRING_SERVICE_NAME, key)
        assert stored is None

    def test_delete_token_raises_value_error_for_none_service(self) -> None:
        """delete_token should raise ValueError if service is None."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="service must not be None"):
            delete_token(backend, None, "profile")

    def test_delete_token_raises_value_error_for_empty_profile(self) -> None:
        """delete_token should raise ValueError if profile_name is empty."""
        backend = InMemoryKeyringBackend()
        with pytest.raises(ValueError, match="profile_name must not be empty"):
            delete_token(backend, SourceService.YOUTUBE, "")

    def test_delete_token_raises_keyring_error_on_backend_failure(self) -> None:
        """delete_token should raise KeyringError when the keyring backend fails."""
        backend = FailingKeyringBackend()

        with pytest.raises(KeyringError, match="Failed to delete token"):
            delete_token(backend, SourceService.YOUTUBE, "profile")


# ============================================================================
# Test helpers
# ============================================================================


class InMemoryKeyringBackend:
    """A simple in-memory keyring backend for testing."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, str]] = {}

    def set_password(self, service: str, key: str, value: str) -> None:
        if service not in self._data:
            self._data[service] = {}
        self._data[service][key] = value

    def get_password(self, service: str, key: str) -> str | None:
        return self._data.get(service, {}).get(key)

    def delete_password(self, service: str, key: str) -> None:
        if service in self._data:
            self._data[service].pop(key, None)


class FailingKeyringBackend:
    """A keyring backend that always fails."""

    def __init__(self) -> None:
        from keyring.errors import KeyringError
        self._error = KeyringError

    def set_password(self, service: str, key: str, value: str) -> None:
        raise self._error("Backend failure")

    def get_password(self, service: str, key: str) -> str:
        raise self._error("Backend failure")

    def delete_password(self, service: str, key: str) -> None:
        raise self._error("Backend failure")
