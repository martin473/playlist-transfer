"""Schema initialization and migration utilities for playlist-bridge."""

import shutil
from pathlib import Path
from typing import Optional

from sqlalchemy import inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from playlist_bridge.persistence.base import Base

# Import all models to ensure they are registered with Base.metadata
from playlist_bridge.persistence import models  # noqa: F401


class SchemaInitializationError(Exception):
    """Raised when schema initialization fails."""

    pass


def initialize_schema(engine: Engine) -> None:
    """
    Initialize a fresh database schema using the declarative metadata.

    This function creates all tables defined in the Base metadata. If the
    database already contains tables, existing tables are left untouched
    (SQLAlchemy's create_all is idempotent).

    Args:
        engine: SQLAlchemy Engine connected to the target database.

    Raises:
        SchemaInitializationError: If table creation fails due to a
            SQLAlchemy error or other unexpected condition.

    Note:
        This function is intended for fresh schema creation and simple
        migrations. For complex migrations, use Alembic.
    """
    try:
        # Create all tables defined in the metadata
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        raise SchemaInitializationError(f"Failed to create schema: {e}") from e


def create_backup(db_path: Path, backup_dir: Optional[Path] = None) -> Path:
    """
    Create a backup of a SQLite database file.

    Args:
        db_path: Path to the SQLite database file to back up.
        backup_dir: Directory where the backup should be stored. If None,
            the backup is created in the same directory as db_path with
            a timestamp suffix.

    Returns:
        Path to the created backup file.

    Raises:
        FileNotFoundError: If the database file does not exist.
        OSError: If the backup cannot be created due to filesystem errors.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"Database file not found: {db_path}")

    # Determine backup path
    if backup_dir is None:
        backup_dir = db_path.parent
    else:
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)

    import time
    timestamp = int(time.time())
    backup_name = f"{db_path.stem}_backup_{timestamp}{db_path.suffix}"
    backup_path = backup_dir / backup_name

    try:
        shutil.copy2(db_path, backup_path)
        return backup_path
    except OSError as e:
        raise OSError(f"Failed to create backup at {backup_path}: {e}") from e


def get_existing_tables(engine: Engine) -> set[str]:
    """
    Get the set of table names currently present in the database.

    Args:
        engine: SQLAlchemy Engine connected to the target database.

    Returns:
        Set of table names (lowercase) that exist in the database.
    """
    inspector = inspect(engine)
    return set(inspector.get_table_names())


def upgrade_schema(engine: Engine, database_file: Path) -> None:
    """
    Upgrade the database schema to the latest Alembic revision.

    This function creates a timestamped backup of the database before upgrading
    if the database is non-empty (has at least one table). The backup is stored
    in the same directory as the database file and is never deleted.

    Args:
        engine: SQLAlchemy Engine connected to the target database.
        database_file: Path to the SQLite database file.

    Raises:
        FileNotFoundError: If the database file does not exist.
        OSError: If the backup cannot be created due to filesystem errors.
        RuntimeError: If the Alembic upgrade fails.

    Note:
        Backups are created with the format: {db_name}_backup_{timestamp}.db
        and are never automatically deleted.
    """
    import os
    from alembic.config import Config
    from alembic import command

    # Check if the database file exists
    if not database_file.exists():
        raise FileNotFoundError(f"Database file not found: {database_file}")

    # Check if the database has any tables (non-empty)
    existing_tables = get_existing_tables(engine)
    if existing_tables:
        # Database is non-empty, create a backup before upgrading
        create_backup(database_file)

    # Create Alembic config and run upgrade to head
    try:
        # Set the DATABASE_URL environment variable for Alembic to use
        # This is needed because migrations/env.py reads from os.environ
        os.environ["DATABASE_URL"] = str(engine.url)

        alembic_cfg = Config("alembic.ini")
        # Also set the sqlalchemy.url option as a fallback
        alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url))

        # Run the upgrade to head
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        raise RuntimeError(f"Failed to upgrade schema: {e}") from e


def table_exists(engine: Engine, table_name: str) -> bool:
    """
    Check if a specific table exists in the database.

    Args:
        engine: SQLAlchemy Engine connected to the target database.
        table_name: Name of the table to check.

    Returns:
        True if the table exists, False otherwise.
    """
    return table_name in get_existing_tables(engine)
