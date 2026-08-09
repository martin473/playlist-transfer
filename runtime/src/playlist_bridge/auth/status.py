"""Authentication status aggregation for source and destination services."""

from typing import Literal
from pydantic import BaseModel

from playlist_bridge.domain.enums import SourceService, DestinationService


class AuthStatus(BaseModel):
    """Authentication status for a specific service and profile.

    Represents the result of checking authentication state for a provider
    (YouTube as source or Spotify as destination) with a given profile name.

    Attributes:
        service: The service being checked (SourceService or DestinationService).
        profile_name: The name of the profile being checked.
        state: The authentication state - one of:
            - authenticated: Valid credentials exist and are usable.
            - missing: No credentials found for this profile.
            - expired_refreshable: Token expired but refresh token available.
            - invalid: Credentials exist but are invalid/corrupted.
        provider_user_id: The provider's user ID if authenticated, else None.
        display_name: The display name if authenticated, else None.
        safe_message: A user-safe message explaining the status, if any.
    """

    service: SourceService | DestinationService
    profile_name: str
    state: Literal["authenticated", "missing", "expired_refreshable", "invalid"]
    provider_user_id: str | None = None
    display_name: str | None = None
    safe_message: str | None = None

    model_config = {
        "frozen": True,
        "extra": "forbid",
    }
