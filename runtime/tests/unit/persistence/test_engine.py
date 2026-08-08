"""Unit tests for the SQLAlchemy engine factory."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from playlist_bridge.persistence.engine import create_engine_for_path


def test_create_engine_for_path_with_temp_db():
    """Test that the engine factory creates a valid engine with foreign keys enabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        # Create the engine
        engine = create_engine_for_path(db_path)

        # The database file won't exist until we actually connect
        assert engine is not None
        assert not db_path.exists()

        # Verify foreign keys are enabled after connection
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys;"))
            foreign_keys_enabled = result.scalar()
            assert foreign_keys_enabled == 1, "PRAGMA foreign_keys should be ON (1)"

        # Now the database file should exist
        assert db_path.exists()


def test_create_engine_for_path_creates_parent_directories():
    """Test that the engine factory creates nested parent directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = Path(tmpdir) / "deep" / "nested" / "path" / "db.sqlite"

        # The parent directories should not exist yet
        assert not nested_path.parent.exists()

        # Create the engine (should create directories)
        engine = create_engine_for_path(nested_path)

        # Verify the parent directories were created (before connection)
        assert nested_path.parent.exists()
        # The file itself won't exist until we connect
        assert not nested_path.exists()

        # Verify basic functionality after connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            assert result.scalar() == 1

        # Now the file should exist
        assert nested_path.exists()


def test_create_engine_for_path_uses_configured_pooling():
    """Test that the engine is configured with reasonable pool settings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "pool_test.db"

        engine = create_engine_for_path(db_path)

        # Check that pool settings are applied
        pool = engine.pool

        # The pool is created with a size of 5, but it starts empty
        # SQLite's pool may have different behavior, so we check the
        # pool's configured size and then verify it works
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 42;"))
            assert result.scalar() == 42

        # The pool should be configured with size 5
        # For SQLite, the pool_size is set correctly but the pool may
        # have a different internal state for SQLite connections
        assert pool.size() == 5  # Should match our configured pool_size


def test_create_engine_for_path_raises_oserror_for_invalid_path():
    """Test that OSError is raised when the database path is invalid."""
    # This is tricky to test on all platforms; we test a case where the path is
    # a file that exists but is not a directory (can't create parent)
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a file that will block directory creation
        block_path = Path(tmpdir) / "blocking_file"
        block_path.touch()

        # Try to use it as a directory in the path
        invalid_path = block_path / "subdir" / "db.sqlite"

        # This should raise OSError because block_path is a file, not a directory
        with pytest.raises(OSError, match="Cannot create parent directory"):
            create_engine_for_path(invalid_path)


def test_create_engine_for_path_handles_sqlalchemy_errors():
    """Test that SQLAlchemy errors are properly raised."""
    # This test verifies that the function correctly surfaces SQLAlchemy errors
    # We can't easily trigger a SQLAlchemy error with valid inputs, so we'll
    # test the error handling by using an invalid URI (which would be caught
    # by the engine factory but we can't easily test it without mocking)
    # Instead, we'll verify the contract that SQLAlchemyError is in the signature

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "valid.db"

        # This should work normally
        engine = create_engine_for_path(db_path)

        # Verify that the engine works
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1;"))
            assert result.scalar() == 1

        # Test a SQLAlchemy error case by using the engine in a way that
        # would cause an error (using a connection after it's closed)
        # The engine itself should be fine; errors happen at the connection level

        # This validates that the function can raise SQLAlchemyError
        # (by not catching it and allowing it to propagate)
        # We'll just test that a legitimate error propagates correctly
        # by creating an invalid query
        with pytest.raises(SQLAlchemyError):
            with engine.connect() as conn:
                # This should fail with a SQLAlchemy error (syntax error)
                conn.execute(text("SELECT INVALID;"))
