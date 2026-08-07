"""Job runner and job ID generation for playlist-bridge."""

import uuid
from typing import Union


def new_job_id() -> str:
    """Generate a new unique job ID.

    Returns:
        A string containing a UUID4 hex representation safe for use in filenames
        and filesystem paths.

    Examples:
        >>> job_id = new_job_id()
        >>> isinstance(job_id, str)
        True
        >>> len(job_id) == 32
        True
        >>> all(c.isalnum() for c in job_id)
        True
    """
    return uuid.uuid4().hex


def validate_job_id(job_id: Union[str, None]) -> bool:
    """Validate that a job ID is a properly formed UUID4 hex string.

    Args:
        job_id: The job ID string to validate, or None.

    Returns:
        True if the job ID is a 32-character hex string, False otherwise.

    Examples:
        >>> validate_job_id(new_job_id())
        True
        >>> validate_job_id("invalid")
        False
        >>> validate_job_id(None)
        False
        >>> validate_job_id("1234567890abcdef1234567890abcdef")
        True
    """
    if not job_id or not isinstance(job_id, str):
        return False
    if len(job_id) != 32:
        return False
    try:
        int(job_id, 16)
        return True
    except ValueError:
        return False
