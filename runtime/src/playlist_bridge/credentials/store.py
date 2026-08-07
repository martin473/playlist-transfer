"""Credential storage operations.

This module provides functions for generating deterministic key names
for credential storage in the system keyring.
"""

import hashlib
from typing import Union

from playlist_bridge.domain import DestinationService, SourceService

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
