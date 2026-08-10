"""Spotify authentication using PKCE OAuth flow."""

from typing import Optional

from spotipy import Spotify, SpotifyPKCE
from spotipy.oauth2 import SpotifyOauthError

from playlist_bridge.credentials.store import KeyringCacheHandler
from playlist_bridge.domain.enums import DestinationService, SourceService
from playlist_bridge.domain.models import AccountProfile
from playlist_bridge.ports import AccountProfileRepository, CredentialStore
from playlist_bridge.providers.errors import (
    AuthenticationRequired,
    InvalidProviderResponse,
    PermissionDenied,
    RateLimited,
    TemporaryProviderFailure,
)
from playlist_bridge.settings import SpotifyOAuthSettings


def create_spotify_pkce_manager(
    settings: SpotifyOAuthSettings,
    cache_handler: KeyringCacheHandler,
    open_browser: bool = True,
) -> SpotifyPKCE:
    """Create a Spotify PKCE authentication manager.

    Args:
        settings: Spotify OAuth settings containing client_id, redirect_uri, and scopes.
        cache_handler: KeyringCacheHandler for token storage and retrieval.
        open_browser: Whether to open the browser automatically for authorization.
            Defaults to True.

    Returns:
        SpotifyPKCE: A configured Spotify PKCE OAuth manager.

    Raises:
        ValueError: If settings or cache_handler is invalid.
    """
    if settings is None:
        raise ValueError("settings must not be None")
    if cache_handler is None:
        raise ValueError("cache_handler must not be None")

    # Extract scopes as a list for SpotifyPKCE
    scopes_list = list(settings.scopes) if settings.scopes else []

    return SpotifyPKCE(
        client_id=settings.client_id,
        redirect_uri=settings.redirect_uri,
        scope=scopes_list,
        cache_handler=cache_handler,
        open_browser=open_browser,
    )


def authenticate_spotify_profile(
    profile_name: str,
    settings: SpotifyOAuthSettings,
    profiles: AccountProfileRepository,
    credentials: CredentialStore,
    open_browser: bool = True,
) -> AccountProfile:
    """Authenticate a Spotify profile using PKCE OAuth flow.

    This function triggers the Spotify authorization flow, handles the loopback
    callback, and stores the resulting credentials and profile information.

    Args:
        profile_name: The name of the profile to authenticate (e.g., "default").
        settings: Spotify OAuth settings containing client_id, redirect_uri, and scopes.
        profiles: Repository for storing account profile information.
        credentials: Credential store for OAuth token storage.
        open_browser: Whether to open the browser automatically for authorization.
            Defaults to True.

    Returns:
        AccountProfile: The authenticated account profile.

    Raises:
        AuthenticationRequired: If authentication fails or is incomplete.
        PermissionDenied: If the user denies permission or lacks access.
        InvalidProviderResponse: If Spotify returns an invalid response.
        ValueError: If settings or required arguments are invalid.
    """
    if not profile_name or not profile_name.strip():
        raise ValueError("profile_name must not be empty")
    if settings is None:
        raise ValueError("settings must not be None")
    if profiles is None:
        raise ValueError("profiles repository must not be None")
    if credentials is None:
        raise ValueError("credentials store must not be None")

    # Create a cache handler that uses the CredentialStore
    cache_handler = KeyringCacheHandler(credentials)

    # Create the Spotify PKCE manager
    sp_pkce = create_spotify_pkce_manager(
        settings=settings,
        cache_handler=cache_handler,
        open_browser=open_browser,
    )

    try:
        # Get authorization (this handles the loopback callback)
        # The get_authorization_url method opens the browser and waits for the callback
        token_info = sp_pkce.get_access_token(as_dict=True)

        if not token_info:
            raise AuthenticationRequired(
                service="spotify",
                operation="authenticate",
                safe_message="Failed to obtain Spotify access token",
            )

        # Get the current user's profile
        import spotipy
        sp_client = spotipy.Spotify(auth=token_info.get("access_token"))
        user_info = sp_client.me()

        if not user_info:
            raise InvalidProviderResponse(
                service="spotify",
                operation="authenticate",
                safe_message="Spotify returned empty user profile",
            )

        # Extract user information
        account_id = user_info.get("id")
        display_name = user_info.get("display_name") or user_info.get("id", "Unknown")
        email = user_info.get("email")
        username = user_info.get("display_name")
        profile_url = user_info.get("external_urls", {}).get("spotify")

        if not account_id:
            raise InvalidProviderResponse(
                service="spotify",
                operation="authenticate",
                safe_message="Spotify user profile missing 'id' field",
            )

        # Create the account profile
        account_profile = AccountProfile(
            provider="spotify",
            account_id=account_id,
            display_name=display_name,
            email=email,
            username=username,
            profile_url=profile_url,
        )

        # Save the profile to the repository
        try:
            saved_profile = profiles.save(account_profile)
        except Exception as e:
            raise InvalidProviderResponse(
                service="spotify",
                operation="save_profile",
                safe_message=f"Failed to save account profile: {e}",
            )

        return saved_profile

    except SpotifyOauthError as e:
        if "access_denied" in str(e).lower():
            raise PermissionDenied(
                service="spotify",
                operation="authenticate",
                safe_message="User denied Spotify authorization",
            ) from e


def probe_spotify_identity(client: Spotify, profile_name: str) -> AccountProfile:
    """Probe the identity of the authenticated Spotify user.

    Args:
        client: An authenticated Spotify client instance.
        profile_name: The name of the profile being probed.

    Returns:
        AccountProfile: The account profile containing provider user ID and display name.

    Raises:
        AuthenticationRequired: If the client is not authenticated.
        PermissionDenied: If the authenticated user lacks permission to access their profile.
        RateLimited: If the Spotify API rate limit is exceeded.
        InvalidProviderResponse: If Spotify returns an invalid or malformed response.
        TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
    """
    try:
        # Get the current user's profile
        user_info = client.me()

        if not user_info:
            raise InvalidProviderResponse(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify returned empty user profile",
            )

        # Extract user information
        account_id = user_info.get("id")
        display_name = user_info.get("display_name") or user_info.get("id", "Unknown")

        if not account_id:
            raise InvalidProviderResponse(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify user profile missing 'id' field",
            )

        # Return the account profile
        return AccountProfile(
            profile_name=profile_name,
            service="spotify",
            provider_user_id=account_id,
            display_name=display_name,
        )

    except SpotifyOauthError as e:
        # Handle OAuth-specific errors
        error_msg = str(e).lower()
        if "access_denied" in error_msg:
            raise PermissionDenied(
                service="spotify",
                operation="probe_identity",
                safe_message="User denied access to Spotify profile",
            ) from e
        elif "rate limit" in error_msg or "rate_limit" in error_msg:
            raise RateLimited(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify API rate limit exceeded",
            ) from e
        else:
            raise AuthenticationRequired(
                service="spotify",
                operation="probe_identity",
                safe_message=f"Spotify authentication failed: {e}",
            ) from e
    except Exception as e:
        # Re-raise known error types
        if isinstance(e, (AuthenticationRequired, PermissionDenied, RateLimited, InvalidProviderResponse, TemporaryProviderFailure)):
            raise
        # Handle other exceptions
        raise TemporaryProviderFailure(
            service="spotify",
            operation="probe_identity",
            safe_message=f"Spotify API temporarily unavailable: {e}",
        ) from e
        raise AuthenticationRequired(
            service="spotify",
            operation="authenticate",
            safe_message=f"Spotify authentication failed: {e}",
        ) from e


def probe_spotify_identity(client: Spotify, profile_name: str) -> AccountProfile:
    """Probe the identity of the authenticated Spotify user.

    Args:
        client: An authenticated Spotify client instance.
        profile_name: The name of the profile being probed.

    Returns:
        AccountProfile: The account profile containing provider user ID and display name.

    Raises:
        AuthenticationRequired: If the client is not authenticated.
        PermissionDenied: If the authenticated user lacks permission to access their profile.
        RateLimited: If the Spotify API rate limit is exceeded.
        InvalidProviderResponse: If Spotify returns an invalid or malformed response.
        TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
    """
    try:
        # Get the current user's profile
        user_info = client.me()

        if not user_info:
            raise InvalidProviderResponse(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify returned empty user profile",
            )

        # Extract user information
        account_id = user_info.get("id")
        display_name = user_info.get("display_name") or user_info.get("id", "Unknown")

        if not account_id:
            raise InvalidProviderResponse(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify user profile missing 'id' field",
            )

        # Return the account profile
        return AccountProfile(
            profile_name=profile_name,
            service="spotify",
            provider_user_id=account_id,
            display_name=display_name,
        )

    except SpotifyOauthError as e:
        # Handle OAuth-specific errors
        error_msg = str(e).lower()
        if "access_denied" in error_msg:
            raise PermissionDenied(
                service="spotify",
                operation="probe_identity",
                safe_message="User denied access to Spotify profile",
            ) from e
        elif "rate limit" in error_msg or "rate_limit" in error_msg:
            raise RateLimited(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify API rate limit exceeded",
            ) from e
        else:
            raise AuthenticationRequired(
                service="spotify",
                operation="probe_identity",
                safe_message=f"Spotify authentication failed: {e}",
            ) from e
    except Exception as e:
        # Re-raise known error types
        if isinstance(e, (AuthenticationRequired, PermissionDenied, RateLimited, InvalidProviderResponse, TemporaryProviderFailure)):
            raise
        # Handle other exceptions
        raise TemporaryProviderFailure(
            service="spotify",
            operation="probe_identity",
            safe_message=f"Spotify API temporarily unavailable: {e}",
        ) from e
    except Exception as e:
        if isinstance(e, (AuthenticationRequired, PermissionDenied, InvalidProviderResponse)):
            raise
        raise AuthenticationRequired(
            service="spotify",
            operation="authenticate",
            safe_message=f"Spotify authentication failed: {e}",
        ) from e


def probe_spotify_identity(client: Spotify, profile_name: str) -> AccountProfile:
    """Probe the identity of the authenticated Spotify user.

    Args:
        client: An authenticated Spotify client instance.
        profile_name: The name of the profile being probed.

    Returns:
        AccountProfile: The account profile containing provider user ID and display name.

    Raises:
        AuthenticationRequired: If the client is not authenticated.
        PermissionDenied: If the authenticated user lacks permission to access their profile.
        RateLimited: If the Spotify API rate limit is exceeded.
        InvalidProviderResponse: If Spotify returns an invalid or malformed response.
        TemporaryProviderFailure: If the Spotify API is temporarily unavailable.
    """
    try:
        # Get the current user's profile
        user_info = client.me()

        if not user_info:
            raise InvalidProviderResponse(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify returned empty user profile",
            )

        # Extract user information
        account_id = user_info.get("id")
        display_name = user_info.get("display_name") or user_info.get("id", "Unknown")

        if not account_id:
            raise InvalidProviderResponse(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify user profile missing 'id' field",
            )

        # Return the account profile
        return AccountProfile(
            profile_name=profile_name,
            service="spotify",
            provider_user_id=account_id,
            display_name=display_name,
        )

    except SpotifyOauthError as e:
        # Handle OAuth-specific errors
        error_msg = str(e).lower()
        if "access_denied" in error_msg:
            raise PermissionDenied(
                service="spotify",
                operation="probe_identity",
                safe_message="User denied access to Spotify profile",
            ) from e
        elif "rate limit" in error_msg or "rate_limit" in error_msg:
            raise RateLimited(
                service="spotify",
                operation="probe_identity",
                safe_message="Spotify API rate limit exceeded",
            ) from e
        else:
            raise AuthenticationRequired(
                service="spotify",
                operation="probe_identity",
                safe_message=f"Spotify authentication failed: {e}",
            ) from e
    except Exception as e:
        # Re-raise known error types
        if isinstance(e, (AuthenticationRequired, PermissionDenied, RateLimited, InvalidProviderResponse, TemporaryProviderFailure)):
            raise
        # Handle other exceptions
        raise TemporaryProviderFailure(
            service="spotify",
            operation="probe_identity",
            safe_message=f"Spotify API temporarily unavailable: {e}",
        ) from e
