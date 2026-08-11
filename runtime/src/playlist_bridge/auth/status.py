"""Authentication status aggregation for source and destination services."""

from typing import Literal, Sequence
from pydantic import BaseModel

from playlist_bridge.domain.enums import DestinationService, SourceService
from playlist_bridge.ports import AccountProfileRepository, CredentialStore, CredentialCorruptionError


class AuthStatus(BaseModel):
    """Authentication status for a specific service and profile.

    Represents the result of checking authentication state for a provider
    (YouTube as source or Spotify as destination) with a given profile name.

    Attributes:
        service: The service being checked (SourceService or DestinationService).
        profile_name: The name of the profile being checked.
        state: The authentication state - one of:
            - authenticated: Valid credentials exist and are usable.
            - expired_refreshable: Token expired but refresh token available.
            - invalid: Credentials exist but are invalid/corrupted.
            - missing: No credentials found for this profile.
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


def probe_spotify_auth_status(
    profile_name: str,
    profiles: AccountProfileRepository,
    credentials: CredentialStore,
) -> AuthStatus:
    """Probe the authentication status for a Spotify profile.

    This function checks the authentication state for a given Spotify profile
    without opening a browser or performing interactive authentication.

    Args:
        profile_name: The name of the profile to check.
        profiles: Repository for account profile data.
        credentials: Credential store for OAuth token storage.

    Returns:
        AuthStatus: The authentication status with one of four states:
            - authenticated: Valid credentials exist and the profile is accessible.
            - missing: No credentials found for this profile.
            - expired_refreshable: Token expired but a refresh token is available.
            - invalid: Credentials exist but are corrupted or invalid.

    Raises:
        CredentialCorruptionError: If stored credentials are malformed.
    """
    from playlist_bridge.auth.spotify import probe_spotify_identity
    from playlist_bridge.providers.errors import (
        AuthenticationRequired,
        InvalidProviderResponse,
        PermissionDenied,
        RateLimited,
        TemporaryProviderFailure,
    )

    # Check if credentials exist
    try:
        token_data = credentials.load(DestinationService.SPOTIFY, profile_name)
    except CredentialCorruptionError:
        # Re-raise as-is
        raise
    except Exception as e:
        # Treat any other load error as corruption
        raise CredentialCorruptionError(
            service="spotify",
            profile_name=profile_name,
            safe_message=f"Failed to load Spotify credentials: {e}",
        ) from e

    if token_data is None:
        # No credentials found
        return AuthStatus(
            service=DestinationService.SPOTIFY,
            profile_name=profile_name,
            state="missing",
            safe_message="No Spotify credentials found for this profile",
        )

    # Check if we have a refresh token
    refresh_token = token_data.get("refresh_token")
    has_refresh = refresh_token is not None and str(refresh_token).strip() != ""

    # Try to use the credentials to probe identity
    try:
        # Get access token from token_data
        access_token = token_data.get("access_token")
        if not access_token:
            # No access token - check if refreshable
            if has_refresh:
                return AuthStatus(
                    service=DestinationService.SPOTIFY,
                    profile_name=profile_name,
                    state="expired_refreshable",
                    safe_message="Spotify access token missing but refresh token available",
                )
            else:
                return AuthStatus(
                    service=DestinationService.SPOTIFY,
                    profile_name=profile_name,
                    state="invalid",
                    safe_message="Spotify credentials missing access token",
                )

        # Create a minimal client with the token
        import spotipy
        client = spotipy.Spotify(auth=str(access_token))

        # Probe identity
        profile = probe_spotify_identity(client, profile_name)

        return AuthStatus(
            service=DestinationService.SPOTIFY,
            profile_name=profile_name,
            state="authenticated",
            provider_user_id=profile.provider_user_id,
            display_name=profile.display_name,
            safe_message="Spotify authentication successful",
        )

    except AuthenticationRequired as e:
        # Authentication failed - check if refreshable
        if has_refresh:
            return AuthStatus(
                service=DestinationService.SPOTIFY,
                profile_name=profile_name,
                state="expired_refreshable",
                safe_message=str(e.safe_message) if e.safe_message else "Spotify token expired but refresh available",
            )
        else:
            return AuthStatus(
                service=DestinationService.SPOTIFY,
                profile_name=profile_name,
                state="invalid",
                safe_message=str(e.safe_message) if e.safe_message else "Spotify authentication failed",
            )

    except (PermissionDenied, InvalidProviderResponse, RateLimited, TemporaryProviderFailure) as e:
        # These indicate the credentials are present but the API rejected them
        # or there was a temporary issue
        if has_refresh:
            # If we have a refresh token, the token might be expired but refreshable
            return AuthStatus(
                service=DestinationService.SPOTIFY,
                profile_name=profile_name,
                state="expired_refreshable",
                safe_message=f"Spotify token issue: {e.safe_message if hasattr(e, 'safe_message') else str(e)}",
            )
        else:
            return AuthStatus(
                service=DestinationService.SPOTIFY,
                profile_name=profile_name,
                state="invalid",
                safe_message=f"Spotify credentials invalid: {e.safe_message if hasattr(e, 'safe_message') else str(e)}",
            )

    except Exception as e:
        # Check if it's a spotipy OAuth error
        if hasattr(e, "__class__") and "SpotifyOauthError" in str(e.__class__):
            if has_refresh:
                return AuthStatus(
                    service=DestinationService.SPOTIFY,
                    profile_name=profile_name,
                    state="expired_refreshable",
                    safe_message="Spotify token expired but refresh available",
                )
            else:
                return AuthStatus(
                    service=DestinationService.SPOTIFY,
                    profile_name=profile_name,
                    state="invalid",
                    safe_message="Spotify authentication required",
                )

        # Unexpected error - treat as invalid
        return AuthStatus(
            service=DestinationService.SPOTIFY,
            profile_name=profile_name,
            state="invalid",
            safe_message=f"Spotify credential check failed: {e}",
        )


def probe_youtube_auth_status(
    profile_name: str,
    profiles: AccountProfileRepository,
    credentials: CredentialStore,
) -> AuthStatus:
    """Probe the authentication status for a YouTube profile.

    This function checks the authentication state for a given YouTube profile
    without opening a browser or performing interactive authentication.

    Args:
        profile_name: The name of the profile to check.
        profiles: Repository for account profile data.
        credentials: Credential store for OAuth token storage.

    Returns:
        AuthStatus: The authentication status with one of four states:
            - authenticated: Valid credentials exist and the profile is accessible.
            - missing: No credentials found for this profile.
            - expired_refreshable: Token expired but a refresh token is available.
            - invalid: Credentials exist but are corrupted or invalid.

    Raises:
        CredentialCorruptionError: If stored credentials are malformed.
    """
    from playlist_bridge.auth.youtube import probe_youtube_identity
    from playlist_bridge.providers.errors import (
        AuthenticationRequired,
        InvalidProviderResponse,
        PermissionDenied,
        RateLimited,
        TemporaryProviderFailure,
    )

    # Check if credentials exist
    try:
        token_data = credentials.load(SourceService.YOUTUBE, profile_name)
    except CredentialCorruptionError:
        # Re-raise as-is
        raise
    except Exception as e:
        # Treat any other load error as corruption
        raise CredentialCorruptionError(
            service="youtube",
            profile_name=profile_name,
            safe_message=f"Failed to load YouTube credentials: {e}",
        ) from e

    if token_data is None:
        # No credentials found
        return AuthStatus(
            service=SourceService.YOUTUBE,
            profile_name=profile_name,
            state="missing",
            safe_message="No YouTube credentials found for this profile",
        )

    # Check if we have a refresh token
    refresh_token = token_data.get("refresh_token")
    has_refresh = refresh_token is not None and str(refresh_token).strip() != ""

    # Try to use the credentials to probe identity
    try:
        # Get access token from token_data
        access_token = token_data.get("access_token")
        if not access_token:
            # No access token - check if refreshable
            if has_refresh:
                return AuthStatus(
                    service=SourceService.YOUTUBE,
                    profile_name=profile_name,
                    state="expired_refreshable",
                    safe_message="YouTube access token missing but refresh token available",
                )
            else:
                return AuthStatus(
                    service=SourceService.YOUTUBE,
                    profile_name=profile_name,
                    state="invalid",
                    safe_message="YouTube credentials missing access token",
                )

        # Build a credentials object for the youtube client
        # The youtube module expects a Credentials object with token and refresh_token
        from google.oauth2.credentials import Credentials
        creds = Credentials(
            token=str(access_token),
            refresh_token=str(refresh_token) if refresh_token else None,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=None,  # Not needed for probing with existing token
            client_secret=None,
        )

        # Probe identity
        profile = probe_youtube_identity(creds, profile_name)

        return AuthStatus(
            service=SourceService.YOUTUBE,
            profile_name=profile_name,
            state="authenticated",
            provider_user_id=profile.provider_user_id,
            display_name=profile.display_name,
            safe_message="YouTube authentication successful",
        )

    except AuthenticationRequired as e:
        # Authentication failed - check if refreshable
        if has_refresh:
            return AuthStatus(
                service=SourceService.YOUTUBE,
                profile_name=profile_name,
                state="expired_refreshable",
                safe_message=str(e.safe_message) if e.safe_message else "YouTube token expired but refresh available",
            )
        else:
            return AuthStatus(
                service=SourceService.YOUTUBE,
                profile_name=profile_name,
                state="invalid",
                safe_message=str(e.safe_message) if e.safe_message else "YouTube authentication failed",
            )

    except (PermissionDenied, InvalidProviderResponse, RateLimited, TemporaryProviderFailure) as e:
        # These indicate the credentials are present but the API rejected them
        # or there was a temporary issue
        if has_refresh:
            # If we have a refresh token, the token might be expired but refreshable
            return AuthStatus(
                service=SourceService.YOUTUBE,
                profile_name=profile_name,
                state="expired_refreshable",
                safe_message=f"YouTube token issue: {e.safe_message if hasattr(e, 'safe_message') else str(e)}",
            )
        else:
            return AuthStatus(
                service=SourceService.YOUTUBE,
                profile_name=profile_name,
                state="invalid",
                safe_message=f"YouTube credentials invalid: {e.safe_message if hasattr(e, 'safe_message') else str(e)}",
            )

    except Exception as e:
        # Check if it's an HttpError with a status code
        if hasattr(e, "resp"):
            status_code = getattr(e.resp, "status", None) if hasattr(e, "resp") else None
            if status_code == 401:
                if has_refresh:
                    return AuthStatus(
                        service=SourceService.YOUTUBE,
                        profile_name=profile_name,
                        state="expired_refreshable",
                        safe_message="YouTube token expired but refresh available",
                    )
                else:
                    return AuthStatus(
                        service=SourceService.YOUTUBE,
                        profile_name=profile_name,
                        state="invalid",
                        safe_message="YouTube authentication required",
                    )
            elif status_code is not None:
                if has_refresh:
                    return AuthStatus(
                        service=SourceService.YOUTUBE,
                        profile_name=profile_name,
                        state="expired_refreshable",
                        safe_message=f"YouTube API error: {status_code} - refresh may be needed",
                    )
                else:
                    return AuthStatus(
                        service=SourceService.YOUTUBE,
                        profile_name=profile_name,
                        state="invalid",
                        safe_message=f"YouTube API error: {status_code}",
                    )

        # Unexpected error - treat as invalid
        return AuthStatus(
            service=SourceService.YOUTUBE,
            profile_name=profile_name,
            state="invalid",
            safe_message=f"YouTube credential check failed: {e}",
        )


def get_auth_status(
    service: SourceService | DestinationService,
    profile_name: str,
    profiles: AccountProfileRepository,
    credentials: CredentialStore,
) -> AuthStatus:
    """Get authentication status for a specific service and profile.

    This is the public dispatcher that routes to the appropriate provider probe
    based on the service type. It never opens a browser or performs interactive
    authentication.

    Args:
        service: The service to check (SourceService or DestinationService).
        profile_name: The name of the profile to check.
        profiles: Repository for account profile data.
        credentials: Credential store for OAuth token storage.

    Returns:
        AuthStatus: The authentication status for the given service and profile.

    Raises:
        CredentialCorruptionError: If stored credentials are malformed.
    """
    # Route to the appropriate probe function based on service type
    if service == DestinationService.SPOTIFY:
        return probe_spotify_auth_status(profile_name, profiles, credentials)
    elif service == SourceService.YOUTUBE:
        return probe_youtube_auth_status(profile_name, profiles, credentials)
    else:
        # This should never happen with the current enum types, but handle gracefully
        raise ValueError(f"Unsupported service: {service}")


def get_requested_auth_statuses(
    requests: Sequence[tuple[SourceService | DestinationService, str]],
    profiles: AccountProfileRepository,
    credentials: CredentialStore,
) -> list[AuthStatus]:
    """Get authentication statuses for multiple requested service/profile pairs.

    This function aggregates status checks for multiple service/profile
    requests. It never opens a browser or performs interactive authentication.

    Args:
        requests: A sequence of (service, profile_name) tuples to check.
        profiles: Repository for account profile data.
        credentials: Credential store for OAuth token storage.

    Returns:
        list[AuthStatus]: A list of authentication statuses in the same order
            as the requests. Each status corresponds to the request at the
            same index.

    Raises:
        CredentialCorruptionError: If stored credentials are malformed for any
            of the requests. Note that this may stop processing early.
    """
    results: list[AuthStatus] = []
    for service, profile_name in requests:
        status = get_auth_status(service, profile_name, profiles, credentials)
        results.append(status)
    return results
