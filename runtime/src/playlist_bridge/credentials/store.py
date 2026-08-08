"""Credential storage operations.

This module provides functions for generating deterministic key names
for credential storage in the system keyring, as well as save, load,
and delete operations for token payloads.
"""

import hashlib
import json
from collections.abc import Mapping
from typing import Any, Union

import keyring
from keyring.errors import KeyringError as _KeyringError

from playlist_bridge.domain import DestinationService, SourceService
from playlist_bridge.ports import CredentialCorruptionError, KeyringError

import spotipy.cache_handler as spotipy_cache

# Fixed keyring service name used for all playlist bridge credentials.
KEYRING_SERVICE_NAME = "playlist-bridge"


def credential_key_name(
    service: Union[SourceService, DestinationService], profile_name: str
) -> str:
    """Generate a deterministic key name for storing credentials.

    The key name is derived from the fixed keyring service name, the
    service value, and the profile name. This ensures that:
    - The same inputs produce the same key (deterministic)
    - Different services produce different keys
    - Different profile names produce different keys

    Args:
        service: The service (source or destination) for which credentials
            are being stored.
        profile_name: The name of the profile/account.

    Returns:
        str: A deterministic key name suitable for use with keyring.

    Raises:
        ValueError: If the service is None or profile_name is empty/None.
    """
    if service is None:
        raise ValueError("service must not be None")
    if not profile_name:
        raise ValueError("profile_name must not be empty")

    # Use a hash to create a deterministic but compact key.
    # The full string is: service_name + service.value + profile_name
    input_string = f"{KEYRING_SERVICE_NAME}:{service.value}:{profile_name}"
    hash_digest = hashlib.sha256(input_string.encode("utf-8")).hexdigest()

    # Return a formatted key that includes a prefix for readability.
    return f"{KEYRING_SERVICE_NAME}_{service.value}_{profile_name}_{hash_digest[:8]}"


def save_token(
    backend: keyring.backend.KeyringBackend,
    service: Union[SourceService, DestinationService],
    profile_name: str,
    token_payload: Mapping[str, Any],
) -> None:
    """Save a token payload to the keyring.

    The token is serialized as JSON and stored using the deterministic
    key derived from the service and profile name.

    Args:
        backend: The keyring backend to use for storage.
        service: The service (source or destination) for which credentials
            are being stored.
        profile_name: The name of the profile/account.
        token_payload: The token data to save (must be JSON-serializable).

    Raises:
        ValueError: If service is None, profile_name is empty, or
            token_payload is None.
        KeyringError: If the underlying keyring backend fails.
    """
    if service is None:
        raise ValueError("service must not be None")
    if not profile_name:
        raise ValueError("profile_name must not be empty")
    if token_payload is None:
        raise ValueError("token_payload must not be None")

    try:
        key = credential_key_name(service, profile_name)
        payload_json = json.dumps(dict(token_payload))
        backend.set_password(KEYRING_SERVICE_NAME, key, payload_json)
    except _KeyringError as e:
        raise KeyringError(f"Failed to save token for {service.value}/{profile_name}: {e}") from e
    except TypeError as e:
        raise ValueError(f"Token payload is not JSON-serializable: {e}") from e


def load_token(
    backend: keyring.backend.KeyringBackend,
    service: Union[SourceService, DestinationService],
    profile_name: str,
) -> Mapping[str, Any]:
    """Load a token payload from the keyring.

    Args:
        backend: The keyring backend to use for retrieval.
        service: The service (source or destination) for which credentials
            are being loaded.
        profile_name: The name of the profile/account.

    Returns:
        Mapping[str, Any]: The deserialized token payload.

    Raises:
        ValueError: If service is None or profile_name is empty.
        KeyringError: If the underlying keyring backend fails.
        CredentialCorruptionError: If the stored data is malformed.
    """
    from playlist_bridge.ports import CredentialCorruptionError

    if service is None:
        raise ValueError("service must not be None")
    if not profile_name:
        raise ValueError("profile_name must not be empty")

    try:
        key = credential_key_name(service, profile_name)
        payload_json = backend.get_password(KEYRING_SERVICE_NAME, key)

        if payload_json is None:
            return {}

        payload = json.loads(payload_json)
        if not isinstance(payload, dict):
            raise CredentialCorruptionError(
                service=service.value,
                profile_name=profile_name,
                safe_message="Stored payload is not a JSON object",
            )
        return payload
    except _KeyringError as e:
        raise KeyringError(f"Failed to load token for {service.value}/{profile_name}: {e}") from e
    except json.JSONDecodeError as e:
        raise CredentialCorruptionError(
            service=service.value,
            profile_name=profile_name,
            safe_message=f"Stored payload is not valid JSON: {e}",
        ) from e


def delete_token(
    backend: keyring.backend.KeyringBackend,
    service: Union[SourceService, DestinationService],
    profile_name: str,
) -> None:
    """Delete a token payload from the keyring.

    Args:
        backend: The keyring backend to use for deletion.
        service: The service (source or destination) for which credentials
            are being deleted.
        profile_name: The name of the profile/account.

    Raises:
        ValueError: If service is None or profile_name is empty.
        KeyringError: If the underlying keyring backend fails.
    """
    if service is None:
        raise ValueError("service must not be None")
    if not profile_name:
        raise ValueError("profile_name must not be empty")

    try:
        key = credential_key_name(service, profile_name)
        backend.delete_password(KEYRING_SERVICE_NAME, key)
    except _KeyringError as e:
        raise KeyringError(f"Failed to delete token for {service.value}/{profile_name}: {e}") from e


class KeyringCacheHandler(spotipy_cache.CacheHandler):
    """Spotipy cache handler that delegates to the keyring token store.

    This class implements Spotipy's CacheHandler interface, allowing
    Spotipy to read and write token data using the playlist-bridge
    keyring storage system.

    Attributes:
        service: The service (source or destination) for credentials.
        profile_name: The name of the profile/account.
        store: The credential store backend.
    """

    def __init__(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
        store: keyring.backend.KeyringBackend,
    ) -> None:
        """Initialize the cache handler.

        Args:
            service: The service (source or destination) for credentials.
            profile_name: The name of the profile/account.
            store: The keyring backend to use for storage.
        """
        if service is None:
            raise ValueError("service must not be None")
        if not profile_name:
            raise ValueError("profile_name must not be empty")
        if store is None:
            raise ValueError("store must not be None")

        self.service = service
        self.profile_name = profile_name
        self.store = store

    def get_cached_token(self) -> dict | None:
        """Retrieve the cached token from the keyring.

        Returns:
            dict | None: The token payload if found, None otherwise.
        """
        try:
            payload = load_token(self.store, self.service, self.profile_name)
            # load_token returns {} for missing tokens, but spotipy expects None
            return payload if payload else None
        except (KeyringError, CredentialCorruptionError):
            # Spotipy expects None when token cannot be retrieved
            return None

    def save_token_to_cache(self, token_info: dict) -> None:
        """Save a token to the keyring.

        Args:
            token_info: The token payload to save.
        """
        if token_info is None:
            # Spotipy may call this with None; treat as no-op
            return

        try:
            save_token(self.store, self.service, self.profile_name, token_info)
        except (KeyringError, ValueError):
            # Re-raise as ValueError to match Spotipy's expected error type
            raise ValueError("Failed to save token to cache")

    def delete_cached_token(self) -> None:
        """Delete the cached token from the keyring.

        Spotipy's CacheHandler interface doesn't define this method, but
        it's a useful addition for our implementation.
        """
        try:
            delete_token(self.store, self.service, self.profile_name)
        except (KeyringError, ValueError):
            # Re-raise as ValueError to match Spotipy's expected error type
            raise ValueError("Failed to delete token from cache")
