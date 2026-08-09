"""YouTube/Google authentication and configuration utilities."""

import json
from pathlib import Path
from typing import Final, Sequence

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from playlist_bridge.ports import CredentialCorruptionError
from playlist_bridge.settings import GoogleOAuthSettings
from playlist_bridge.domain.enums import SourceService
from playlist_bridge.providers.errors import AuthenticationRequired, TemporaryProviderFailure

# Default OAuth scopes for YouTube Data API v3
DEFAULT_YOUTUBE_SCOPES: Final[tuple[str, ...]] = (
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
)

# Default OAuth redirect configuration
DEFAULT_REDIRECT_HOST: Final[str] = "localhost"
DEFAULT_REDIRECT_PORT: Final[int] = 8080


def load_google_client_config(client_secret_path: Path) -> GoogleOAuthSettings:
    """Load Google OAuth client configuration from a client secret JSON file.

    This function validates that the client secret file exists and is readable,
    then returns a GoogleOAuthSettings model with the path and default OAuth
    configuration. The actual parsing of the JSON file is deferred to the
    google-auth-oauthlib library during authentication.

    Args:
        client_secret_path: Path to the installed-application OAuth client
            secret JSON file downloaded from the Google Cloud Console.

    Returns:
        GoogleOAuthSettings: Configured settings with the validated client
            secret path and default OAuth scopes and redirect parameters.

    Raises:
        FileNotFoundError: If client_secret_path does not exist or is not a file.
        ValueError: If client_secret_path is invalid (e.g., not a file).

    Side Effects:
        filesystem_read: Verifies that the client secret file exists and is readable.
    """
    if not client_secret_path.exists():
        raise FileNotFoundError(
            f"Google client secret file not found: {client_secret_path}"
        )

    if not client_secret_path.is_file():
        raise ValueError(
            f"Google client secret path is not a file: {client_secret_path}"
        )

    # Return settings with default scopes and redirect parameters
    return GoogleOAuthSettings(
        client_secret_path=client_secret_path,
        scopes=DEFAULT_YOUTUBE_SCOPES,
        redirect_host=DEFAULT_REDIRECT_HOST,
        redirect_port=DEFAULT_REDIRECT_PORT,
    )


def serialize_google_credentials(credentials: Credentials) -> str:
    """Convert Google credentials to a minimal JSON payload suitable for keyring storage.

    The serialized payload contains only the fields required to reconstruct
    a working Credentials object: token, refresh_token, token_uri, client_id,
    client_secret, and scopes. Fields that are None are omitted from the JSON.

    Args:
        credentials: The Google OAuth2 credentials object to serialize.

    Returns:
        A JSON string containing the minimal credential fields.

    Raises:
        CredentialCorruptionError: If the credentials object cannot be serialized,
            typically because it is missing required fields or contains invalid data.

    Side Effects:
        None: Pure function with no I/O or state mutation.
    """
    try:
        # Build the minimal payload with only the fields that are set
        payload: dict[str, object] = {}

        if credentials.token:
            payload["token"] = credentials.token

        if credentials.refresh_token:
            payload["refresh_token"] = credentials.refresh_token

        if credentials.token_uri:
            payload["token_uri"] = credentials.token_uri

        if credentials.client_id:
            payload["client_id"] = credentials.client_id

        if credentials.client_secret:
            payload["client_secret"] = credentials.client_secret

        # Include scopes if present
        if credentials.scopes is not None:
            # Convert tuple/list to list for JSON serialization
            scopes_list = list(credentials.scopes) if credentials.scopes else []
            # Only include scopes if non-empty to match the test expectation
            if scopes_list:
                payload["scopes"] = scopes_list

        # Ensure we have at least the token field to be usable
        # Ensure we have at least the token field to be usable
        token = payload.get("token")
        if not token:
            raise ValueError("Credentials object has no token field set")

        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False, sort_keys=True)

    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as e:
        safe_message = f"Failed to serialize Google credentials: {type(e).__name__}"
        raise CredentialCorruptionError(
            service="youtube",
            profile_name="unknown",
            safe_message=safe_message,
        ) from e


def deserialize_google_credentials(serialized: str, scopes: Sequence[str]) -> Credentials:
    """Reconstruct Google credentials from a serialized JSON payload.

    The serialized string must be a JSON object containing the fields produced
    by serialize_google_credentials. The scopes parameter provides the
    default scopes if the serialized payload does not contain a scopes field.

    Args:
        serialized: A JSON string containing credential fields.
        scopes: Default scopes to use if the serialized payload lacks scopes.

    Returns:
        A fully-initialized Credentials object.

    Raises:
        CredentialCorruptionError: If the serialized data is malformed,
            missing required fields, or cannot be parsed as JSON.

    Side Effects:
        None: Pure function with no I/O or state mutation.
    """
    try:
        payload = json.loads(serialized)

        if not isinstance(payload, dict):
            raise TypeError(f"Expected dict, got {type(payload).__name__}")

        # The token field is required
        token = payload.get("token")
        if not token or not isinstance(token, str):
            safe_message = "Missing or invalid token field in serialized credentials"
            raise CredentialCorruptionError(
                service="youtube",
                profile_name="unknown",
                safe_message=safe_message,
            )

        # Extract fields with defaults for optional ones
        refresh_token = payload.get("refresh_token")
        if refresh_token is not None and not isinstance(refresh_token, str):
            safe_message = "refresh_token field must be a string"
            raise CredentialCorruptionError(
                service="youtube",
                profile_name="unknown",
                safe_message=safe_message,
            )

        token_uri = payload.get("token_uri")
        if token_uri is not None and not isinstance(token_uri, str):
            safe_message = "token_uri field must be a string"
            raise CredentialCorruptionError(
                service="youtube",
                profile_name="unknown",
                safe_message=safe_message,
            )

        client_id = payload.get("client_id")
        if client_id is not None and not isinstance(client_id, str):
            safe_message = "client_id field must be a string"
            raise CredentialCorruptionError(
                service="youtube",
                profile_name="unknown",
                safe_message=safe_message,
            )

        client_secret = payload.get("client_secret")
        if client_secret is not None and not isinstance(client_secret, str):
            safe_message = "client_secret field must be a string"
            raise CredentialCorruptionError(
                service="youtube",
                profile_name="unknown",
                safe_message=safe_message,
            )

        # Scopes can be a list or tuple
        payload_scopes = payload.get("scopes")
        if payload_scopes is not None:
            if not isinstance(payload_scopes, list):
                safe_message = "scopes field must be a list"
                raise CredentialCorruptionError(
                    service="youtube",
                    profile_name="unknown",
                    safe_message=safe_message,
                )
            if not all(isinstance(s, str) for s in payload_scopes):
                safe_message = "scopes field must contain only strings"
                raise CredentialCorruptionError(
                    service="youtube",
                    profile_name="unknown",
                    safe_message=safe_message,
                )
            # Use the scopes from the payload, falling back to the provided scopes
            # Important: payload_scopes could be an empty list, which we should preserve
            final_scopes = payload_scopes if payload_scopes is not None else list(scopes)
        else:
            final_scopes = list(scopes)

        # Reconstruct the Credentials object
        return Credentials(
            token=token,
            refresh_token=refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=final_scopes,
        )

    except json.JSONDecodeError as e:
        raise CredentialCorruptionError(
            service="youtube",
            profile_name="unknown",
            safe_message=f"Malformed JSON in serialized Google credentials: {str(e)}",
        ) from e
    except (AttributeError, TypeError, ValueError) as e:
        safe_message = f"Failed to deserialize Google credentials: {type(e).__name__}"
        raise CredentialCorruptionError(
            service="youtube",
            profile_name="unknown",
            safe_message=safe_message,
        ) from e


def refresh_google_credentials(
    profile_name: str,
    credentials: CredentialStore,
    request: Request,
) -> Credentials:
    """Refresh expired Google credentials that contain a refresh token.

    This function loads stored credentials for the given profile, checks if they
    are expired and have a refresh token, refreshes them using the provided
    Request object, and persists the refreshed credential payload back to the
    credential store.

    Args:
        profile_name: The name of the profile to refresh credentials for.
        credentials: The credential store to load from and save to.
        request: A google.auth.transport.requests.Request object for the refresh.

    Returns:
        Credentials: The refreshed credentials object.

    Raises:
        AuthenticationRequired: If no credentials are stored for the profile,
            or the stored credentials cannot be refreshed (e.g., no refresh token,
            refresh token expired).
        TemporaryProviderFailure: If the refresh request fails due to a network
            issue or the provider returns a transient error.
        CredentialCorruptionError: If the stored credentials are malformed.

    Side Effects:
        provider_network: Makes a network request to Google's OAuth endpoint.
        os_keychain_write: Writes the refreshed payload back to the keychain.
    """
    from playlist_bridge.auth.youtube import deserialize_google_credentials
    from playlist_bridge.auth.youtube import serialize_google_credentials
    from playlist_bridge.auth.youtube import DEFAULT_YOUTUBE_SCOPES

    # Load stored credentials from the keychain
    payload = credentials.load(SourceService.YOUTUBE, profile_name)
    if payload is None:
        raise AuthenticationRequired(
            service="youtube",
            profile_name=profile_name,
            safe_message=f"No credentials found for profile: {profile_name}",
        )

    # Deserialize the stored payload into a Credentials object
    try:
        # Extract scopes from the payload if present, otherwise use defaults
        scopes = payload.get("scopes", list(DEFAULT_YOUTUBE_SCOPES))
        if not isinstance(scopes, list):
            # If scopes is not a list, use defaults
            scopes = list(DEFAULT_YOUTUBE_SCOPES)

        # Build a Credentials object from the stored payload
        stored_creds = Credentials(
            token=payload.get("token"),
            refresh_token=payload.get("refresh_token"),
            token_uri=payload.get("token_uri"),
            client_id=payload.get("client_id"),
            client_secret=payload.get("client_secret"),
            scopes=scopes,
        )
    except (KeyError, TypeError, ValueError) as e:
        raise CredentialCorruptionError(
            service="youtube",
            profile_name=profile_name,
            safe_message=f"Failed to reconstruct credentials from stored payload: {type(e).__name__}",
        ) from e

    # Check if we have a refresh token
    if stored_creds.refresh_token is None:
        raise AuthenticationRequired(
            service="youtube",
            profile_name=profile_name,
            safe_message=f"No refresh token available for profile: {profile_name}",
        )

    # Check if credentials are already expired
    # Credentials.expired returns True if token is expired or token is None
    if not stored_creds.expired:
        # Credentials are still valid; return them without persisting
        return stored_creds

    # Attempt to refresh the credentials
    try:
        stored_creds.refresh(request)
    except Exception as e:
        # The google-auth library raises various exceptions for refresh failures
        # Map them to appropriate domain errors
        error_message = str(e).lower()
        if "invalid_grant" in error_message or "refresh token" in error_message:
            raise AuthenticationRequired(
                service="youtube",
                profile_name=profile_name,
                safe_message=f"Failed to refresh credentials: refresh token invalid or revoked",
            ) from e
        elif "timeout" in error_message or "connection" in error_message:
            raise TemporaryProviderFailure(
                service="youtube",
                profile_name=profile_name,
                safe_message=f"Network error during credential refresh: {type(e).__name__}",
            ) from e
        else:
            # Treat other errors as temporary failures (they may be retried)
            raise TemporaryProviderFailure(
                service="youtube",
                profile_name=profile_name,
                safe_message=f"Failed to refresh credentials: {type(e).__name__}",
            ) from e

    # Serialize the refreshed credentials and save back to the keychain
    try:
        serialized = serialize_google_credentials(stored_creds)
        # Re-parse to get the payload dictionary
        refreshed_payload = json.loads(serialized)
        credentials.save(SourceService.YOUTUBE, profile_name, refreshed_payload)
    except (CredentialCorruptionError, json.JSONDecodeError) as e:
        # Re-raise CredentialCorruptionError as-is
        if isinstance(e, CredentialCorruptionError):
            raise
        raise CredentialCorruptionError(
            service="youtube",
            profile_name=profile_name,
            safe_message=f"Failed to serialize refreshed credentials: {type(e).__name__}",
        ) from e

    return stored_creds
