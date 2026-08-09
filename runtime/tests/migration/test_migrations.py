"""Tests for schema initialization and migration utilities."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from playlist_bridge.persistence.base import Base
from playlist_bridge.persistence.migrations import (
    SchemaInitializationError,
    create_backup,
    get_existing_tables,
    initialize_schema,
    table_exists,
)


# Expected tables from the ORM models
EXPECTED_TABLES = {
    "jobs",
    "account_profiles",
    "match_cache",
    "manual_corrections",
    "source_tracks",
    "match_decisions",
}


@pytest.fixture
def temp_db_path():
    """Create a temporary SQLite database file path."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    # Clean up after test
    if path.exists():
        path.unlink()


@pytest.fixture
def temp_engine(temp_db_path):
    """Create a SQLAlchemy engine for a temporary database."""
    engine = create_engine(f"sqlite:///{temp_db_path}")
    yield engine
    engine.dispose()


class TestInitializeSchema:
    """Tests for the initialize_schema function."""

    def test_initializes_all_expected_tables(self, temp_engine, temp_db_path):
        """Test that initialize_schema creates all expected tables exactly once."""
        # Verify database is empty
        inspector = inspect(temp_engine)
        assert set(inspector.get_table_names()) == set()

        # Initialize schema
        initialize_schema(temp_engine)

        # Verify all expected tables exist
        inspector = inspect(temp_engine)
        actual_tables = set(inspector.get_table_names())
        assert actual_tables == EXPECTED_TABLES

        # Verify each table has the expected columns (basic check)
        for table_name in EXPECTED_TABLES:
            columns = inspector.get_columns(table_name)
            assert len(columns) > 0, f"Table {table_name} has no columns"

    def test_initialize_schema_is_idempotent(self, temp_engine):
        """Test that calling initialize_schema twice has no harmful effects."""
        # First initialization
        initialize_schema(temp_engine)
        inspector = inspect(temp_engine)
        tables_after_first = set(inspector.get_table_names())

        # Second initialization
        initialize_schema(temp_engine)
        tables_after_second = set(inspector.get_table_names())

        # Tables should be identical
        assert tables_after_first == tables_after_second == EXPECTED_TABLES

    def test_schema_contains_foreign_key_constraints(self, temp_engine):
        """Test that foreign key constraints are present."""
        initialize_schema(temp_engine)

        inspector = inspect(temp_engine)
        # Check that source_tracks has a foreign key to jobs
        foreign_keys = inspector.get_foreign_keys("source_tracks")
        job_fk_found = any(
            fk.get("referred_table") == "jobs" for fk in foreign_keys
        )
        assert job_fk_found, "source_tracks should have foreign key to jobs"

        # Check that match_decisions has a foreign key to jobs
        foreign_keys = inspector.get_foreign_keys("match_decisions")
        job_fk_found = any(
            fk.get("referred_table") == "jobs" for fk in foreign_keys
        )
        assert job_fk_found, "match_decisions should have foreign key to jobs"

    def test_schema_contains_unique_constraints(self, temp_engine):
        """Test that unique constraints are present."""
        initialize_schema(temp_engine)

        inspector = inspect(temp_engine)

        # Check unique constraints on account_profiles
        unique_constraints = inspector.get_unique_constraints("account_profiles")
        unique_names = {uc.get("name") for uc in unique_constraints}
        assert "uq_service_profile_name" in unique_names

        # Check unique constraint on match_cache
        unique_constraints = inspector.get_unique_constraints("match_cache")
        unique_names = {uc.get("name") for uc in unique_constraints}
        assert "uq_match_cache_source_fingerprint" in unique_names

    def test_raises_error_on_invalid_engine(self):
        """Test that initialize_schema raises SchemaInitializationError on failure."""
        # Create an engine with an invalid URI
        invalid_engine = create_engine("sqlite:///invalid/path/that/does/not/exist/db.db")

        with pytest.raises(SchemaInitializationError):
            initialize_schema(invalid_engine)

        invalid_engine.dispose()

    def test_initializes_tables_with_correct_columns(self, temp_engine):
        """Test that tables have the expected columns."""
        initialize_schema(temp_engine)
        inspector = inspect(temp_engine)

        # Check jobs table columns
        job_columns = {col["name"] for col in inspector.get_columns("jobs")}
        expected_job_columns = {
            "id",
            "request_json",
            "state",
            "source_playlist_id",
            "destination_playlist_id",
            "source_track_count",
            "match_checkpoint",
            "write_checkpoint",
            "verification_checkpoint",
            "created_at",
            "updated_at",
            "last_error",
            "lease_holder",
            "lease_expires_at",
            "lease_heartbeat_at",
            "row_version",
        }
        assert expected_job_columns.issubset(job_columns)

        # Check match_cache table columns
        cache_columns = {col["name"] for col in inspector.get_columns("match_cache")}
        expected_cache_columns = {
            "id",
            "source_fingerprint",
            "spotify_track_id",
            "confidence",
            "origin",
            "last_verified_at",
            "created_at",
            "updated_at",
        }
        assert expected_cache_columns.issubset(cache_columns)


class TestGetExistingTables:
    """Tests for the get_existing_tables function."""

    def test_returns_empty_set_for_empty_database(self, temp_engine):
        """Test that get_existing_tables returns empty set for empty database."""
        tables = get_existing_tables(temp_engine)
        assert tables == set()

    def test_returns_all_tables_after_initialization(self, temp_engine):
        """Test that get_existing_tables returns all tables after schema init."""
        initialize_schema(temp_engine)
        tables = get_existing_tables(temp_engine)
        assert tables == EXPECTED_TABLES


class TestTableExists:
    """Tests for the table_exists function."""

    def test_returns_false_for_nonexistent_table(self, temp_engine):
        """Test that table_exists returns False for tables that don't exist."""
        assert not table_exists(temp_engine, "nonexistent_table")

    def test_returns_true_for_existing_table(self, temp_engine):
        """Test that table_exists returns True for existing tables."""
        initialize_schema(temp_engine)
        for table_name in EXPECTED_TABLES:
            assert table_exists(temp_engine, table_name)


class TestCreateBackup:
    """Tests for the create_backup function."""

    def test_creates_backup_file(self, temp_db_path):
        """Test that create_backup creates a backup file."""
        # Create a simple database file
        temp_db_path.touch()

        backup_path = create_backup(temp_db_path)
        assert backup_path.exists()
        assert backup_path != temp_db_path
        assert backup_path.suffix == temp_db_path.suffix

        # Clean up backup
        backup_path.unlink()

    def test_backup_has_correct_content(self, temp_db_path):
        """Test that the backup file contains the same content."""
        # Create a database with some content
        engine = create_engine(f"sqlite:///{temp_db_path}")
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER)"))
            conn.execute(text("INSERT INTO test VALUES (1)"))
            conn.commit()
        engine.dispose()

        # Create backup
        backup_path = create_backup(temp_db_path)

        # Verify backup contains the same data
        backup_engine = create_engine(f"sqlite:///{backup_path}")
        with backup_engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM test"))
            rows = result.fetchall()
            assert len(rows) == 1
            assert rows[0][0] == 1
        backup_engine.dispose()

        # Clean up
        backup_path.unlink()

    def test_raises_error_if_database_not_found(self):
        """Test that create_backup raises FileNotFoundError if db doesn't exist."""
        non_existent = Path("/tmp/nonexistent_db_12345.db")
        with pytest.raises(FileNotFoundError):
            create_backup(non_existent)

    def test_respects_backup_directory(self, temp_db_path):
        """Test that create_backup respects the backup_dir parameter."""
        temp_db_path.touch()

        backup_dir = Path(tempfile.mkdtemp())
        backup_path = create_backup(temp_db_path, backup_dir=backup_dir)

        assert backup_path.parent == backup_dir
        assert backup_path.exists()

        # Clean up
        backup_path.unlink()
        backup_dir.rmdir()
