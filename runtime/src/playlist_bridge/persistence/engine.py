"""SQLAlchemy engine factory for playlist-bridge."""

from pathlib import Path
from typing import Final

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


#: Default connection pool size for SQLite.
_POOL_SIZE: Final[int] = 5

#: Maximum number of connections to allow before pruning.
_MAX_OVERFLOW: Final[int] = 10

#: Timeout for acquiring a connection from the pool (seconds).
_POOL_TIMEOUT: Final[int] = 30

#: Timeout for SQLite database operations (milliseconds).
_SQLITE_TIMEOUT_MS: Final[int] = 10000


def create_engine_for_path(path: Path) -> Engine:
    """
    Create a SQLAlchemy engine for a SQLite database at the given path.

    The engine is configured with:
        - Foreign key enforcement enabled via PRAGMA.
        - Bounded connection pooling.
        - A reasonable SQLite timeout.

    Args:
        path: Filesystem path to the SQLite database file.

    Returns:
        A configured SQLAlchemy Engine instance.

    Raises:
        OSError: If the parent directory cannot be created or accessed.
        SQLAlchemyError: For SQLAlchemy-specific errors during engine creation.
    """
    # Ensure the parent directory exists
    parent_dir = path.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OSError(f"Cannot create parent directory for database: {parent_dir}") from e

    # SQLite URI with absolute path
    uri = f"sqlite:///{path.absolute()}"

    # Configure the engine with pooling and timeouts
    engine = create_engine(
        uri,
        pool_size=_POOL_SIZE,
        max_overflow=_MAX_OVERFLOW,
        pool_timeout=_POOL_TIMEOUT,
        connect_args={
            "timeout": _SQLITE_TIMEOUT_MS // 1000,  # SQLite timeout in seconds
            "check_same_thread": False,  # Allow cross-thread usage
        },
    )

    # Enable foreign key enforcement for all connections
    # Use a function that's compatible with SQLAlchemy's event system
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()

    # Register the event listener
    from sqlalchemy import event
    event.listen(engine, "connect", _enable_foreign_keys)

    return engine
