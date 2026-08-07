"""Provider error types for playlist transfer operations."""


class ProviderError(Exception):
    """Base error for provider-related failures.

    Attributes:
        service: The provider service name (e.g., 'spotify', 'youtube').
        operation: The operation that failed (e.g., 'search', 'playlist_create').
        safe_message: A user-facing message that does not contain secrets.
    """

    def __init__(self, service: str, operation: str, safe_message: str) -> None:
        self.service = service
        self.operation = operation
        self.safe_message = safe_message
        super().__init__(safe_message)

    def __str__(self) -> str:
        return f"[{self.service}] {self.operation}: {self.safe_message}"


class AuthenticationRequired(ProviderError):
    """Raised when authentication is required but missing or invalid.

    This error indicates that the provider requires valid credentials
    to perform the requested operation.
    """

    def __init__(self, service: str, operation: str, safe_message: str) -> None:
        super().__init__(service, operation, safe_message)


class PermissionDenied(ProviderError):
    """Raised when the authenticated user lacks permission for an operation.

    This error indicates that the provider rejected the request because
    the authenticated user does not have the required permissions.
    """

    def __init__(self, service: str, operation: str, safe_message: str) -> None:
        super().__init__(service, operation, safe_message)


class ProviderNotFound(ProviderError):
    """Raised when a requested resource is not found.

    This error indicates that the provider could not locate the
    requested resource (e.g., playlist, track, or video).
    """

    def __init__(self, service: str, operation: str, safe_message: str) -> None:
        super().__init__(service, operation, safe_message)


class RateLimited(ProviderError):
    """Raised when a provider rate limit is exceeded.

    This error indicates that the provider has rejected the request
    because the application has exceeded the allowed rate of requests.
    """

    def __init__(self, service: str, operation: str, safe_message: str) -> None:
        super().__init__(service, operation, safe_message)
