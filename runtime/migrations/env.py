"""Alembic migration environment for playlist-bridge.

This environment uses the model metadata from playlist_bridge.persistence.base
and supports a deterministic SQLite URL supplied at runtime.
"""

import os
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine, pool

# Import the Base metadata from the application
from playlist_bridge.persistence.base import Base

# Import all models to ensure they are registered with Base.metadata
import playlist_bridge.persistence.models  # noqa: F401

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
# for 'autogenerate' support
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_sqlite_url() -> str:
    """Get a deterministic SQLite URL supplied at runtime.

    The URL can be provided via the DATABASE_URL environment variable,
    or defaults to an in-memory SQLite database for testing.
    """
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    # Default to an in-memory database for testing
    return "sqlite:///playlist-bridge.db"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_sqlite_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Ensure the directory for the database exists
    url = get_sqlite_url()
    if url.startswith("sqlite:///") and not url.startswith("sqlite:///:memory:"):
        db_path_str = url.replace("sqlite:///", "")
        if db_path_str:
            db_path = Path(db_path_str)
            db_path.parent.mkdir(parents=True, exist_ok=True)

    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
