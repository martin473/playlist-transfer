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
