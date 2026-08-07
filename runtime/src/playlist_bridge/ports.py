"""Port interfaces for the playlist bridge.

This module defines service-neutral protocol interfaces that hide concrete
implementations (keyring, SQLAlchemy) from orchestration and CLI code.
"""

from typing import Any, Mapping, Protocol, Union, runtime_checkable

from playlist_bridge.domain.enums import DestinationService, SourceService


# ============================================================================
# Error types
# ============================================================================


class CredentialCorruptionError(Exception):
    """Raised when stored credentials are malformed or cannot be deserialized.

    Attributes:
        service: The service name (e.g., "spotify", "youtube").
        profile_name: The profile name that was being accessed.
        safe_message: A human-readable message safe for logging/display.
    """

    def __init__(
        self,
        service: str,
        profile_name: str,
        safe_message: str,
    ) -> None:
        self.service = service
        self.profile_name = profile_name
        self.safe_message = safe_message
        super().__init__(f"Credential corruption for {service}/{profile_name}: {safe_message}")


class KeyringError(Exception):
    """Raised when the underlying keyring backend fails.

    This is a generic error for keyring read/write/delete failures.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class IntegrityError(Exception):
    """Raised when a database integrity constraint is violated.

    This is a domain-level error that wraps SQLAlchemy integrity errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


# ============================================================================
# Protocol: CredentialStore
# ============================================================================


@runtime_checkable
class CredentialStore(Protocol):
    """Service-neutral credential protocol.

    The CredentialStore hides the concrete keyring backend (e.g., macOS
    Keychain, Windows Credential Manager, libsecret) and provides typed
    save, load, and delete operations for OAuth tokens and other credentials.

    Implementations must:
        - Raise CredentialCorruptionError when stored data is malformed.
        - Raise KeyringError when the underlying keyring backend fails.
        - Never log or return raw credential secrets in error messages.
        - Store token_payload as a serializable mapping (dict[str, Any]).

    The service parameter must be a SourceService or DestinationService enum
    value. This allows the same store to be used for both source and
    destination authentication.
    """

    def save(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
        token_payload: Mapping[str, Any],
    ) -> None:
        """Save credentials for a given service and profile.

        Args:
            service: The service these credentials are for.
            profile_name: The profile name (e.g., "default", "work").
            token_payload: The credential data to store (e.g., OAuth token dict).

        Raises:
            CredentialCorruptionError: If token_payload cannot be serialized.
            KeyringError: If the keyring backend fails.
        """
        ...

    def load(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
    ) -> dict[str, Any] | None:
        """Load credentials for a given service and profile.

        Args:
            service: The service these credentials are for.
            profile_name: The profile name (e.g., "default", "work").

        Returns:
            The stored credential payload, or None if no credentials exist.

        Raises:
            CredentialCorruptionError: If the stored data is malformed.
            KeyringError: If the keyring backend fails.
        """
        ...

    def delete(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
    ) -> bool:
        """Delete credentials for a given service and profile.

        Args:
            service: The service these credentials are for.
            profile_name: The profile name (e.g., "default", "work").

        Returns:
            True if credentials were deleted, False if they did not exist.

        Raises:
            KeyringError: If the keyring backend fails.
        """
        ...


# ============================================================================
# Protocol: AccountProfileRepository
# ============================================================================

# Forward reference for AccountProfile (defined elsewhere)
# The protocol uses duck typing; the actual type is imported at runtime


@runtime_checkable
class AccountProfileRepository(Protocol):
    """Repository for AccountProfile persistence.

    The AccountProfileRepository hides the SQLAlchemy session and database
    implementation, providing typed save, get, and list operations over
    AccountProfile domain models.

    Implementations must:
        - Raise IntegrityError on constraint violations (e.g., duplicate profile).
        - Return None for get() when the profile does not exist.
        - Return fully populated AccountProfile domain objects.
        - Support filtering by service when listing.

    The service parameter may be None to list all profiles across all services.
    """

    def save(self, profile: Any) -> Any:
        """Save an AccountProfile to the repository.

        Args:
            profile: The AccountProfile instance to save.

        Returns:
            The saved AccountProfile instance (may include generated fields).

        Raises:
            IntegrityError: If a constraint violation occurs.
        """
        ...

    def get(
        self,
        service: Union[SourceService, DestinationService],
        profile_name: str,
    ) -> Any | None:
        """Retrieve an AccountProfile by service and profile name.

        Args:
            service: The service the profile is for.
            profile_name: The profile name (e.g., "default", "work").

        Returns:
            The AccountProfile instance, or None if not found.
        """
        ...

    def list(
        self,
        service: Union[SourceService, DestinationService, None] = None,
    ) -> list[Any]:
        """List AccountProfiles, optionally filtered by service.

        Args:
            service: If provided, only list profiles for this service.
                    If None, list all profiles across all services.

        Returns:
            A list of AccountProfile instances (empty list if none).
        """
        ...
