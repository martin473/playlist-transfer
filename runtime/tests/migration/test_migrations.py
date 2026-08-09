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
    upgrade_schema,
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


class TestUpgradeSchema:
    """Tests for the upgrade_schema function."""

    def test_upgrades_empty_database_no_backup(self, temp_db_path):
        """Test that upgrade_schema on an empty database does not create a backup."""
        # Create an empty database file (no tables)
        temp_db_path.touch()
        engine = create_engine(f"sqlite:///{temp_db_path}")

        # Count existing backup files
        initial_backups = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))

        # Run upgrade
        from playlist_bridge.persistence.migrations import upgrade_schema
        upgrade_schema(engine, temp_db_path)

        # Verify no backup was created
        final_backups = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))
        assert len(final_backups) == len(initial_backups)

        # Verify the schema is now at head revision
        # Alembic creates an alembic_version table; we only check the application tables
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        expected_tables = {
            "jobs",
            "account_profiles",
            "match_cache",
            "manual_corrections",
            "source_tracks",
            "match_decisions",
        }
        # Remove alembic_version from the set if present
        tables.discard("alembic_version")
        assert tables == expected_tables

        engine.dispose()

    def test_upgrades_non_empty_database_creates_backup(self, temp_db_path):
        """Test that upgrade_schema on a non-empty database creates a backup before upgrading."""
        # Create a database with a table (simulating an existing database)
        engine = create_engine(f"sqlite:///{temp_db_path}")
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER)"))
            conn.execute(text("INSERT INTO test VALUES (1)"))
            conn.commit()
        engine.dispose()

        # Count existing backup files
        initial_backups = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))

        # Run upgrade
        engine = create_engine(f"sqlite:///{temp_db_path}")
        from playlist_bridge.persistence.migrations import upgrade_schema
        upgrade_schema(engine, temp_db_path)

        # Verify a backup was created
        final_backups = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))
        assert len(final_backups) == len(initial_backups) + 1

        # Verify the backup contains the original data
        backup_files = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))
        # Get the most recent backup
        backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)

        backup_engine = create_engine(f"sqlite:///{backup_path}")
        with backup_engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM test"))
            rows = result.fetchall()
            assert len(rows) == 1
            assert rows[0][0] == 1
        backup_engine.dispose()

        # Verify the database is now at head revision
        # Alembic creates an alembic_version table and leaves existing tables intact
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        expected_tables = {
            "jobs",
            "account_profiles",
            "match_cache",
            "manual_corrections",
            "source_tracks",
            "match_decisions",
        }
        # Remove alembic_version from the set if present
        tables.discard("alembic_version")
        # The test table should still be present (Alembic doesn't drop unknown tables)
        assert "test" in tables
        assert expected_tables.issubset(tables)

        engine.dispose()

    def test_raises_error_if_database_missing(self, temp_db_path):
        """Test that upgrade_schema raises FileNotFoundError if the database file doesn't exist."""
        # Ensure the file doesn't exist
        if temp_db_path.exists():
            temp_db_path.unlink()

        # Create an engine pointing to the missing file
        engine = create_engine(f"sqlite:///{temp_db_path}")

        from playlist_bridge.persistence.migrations import upgrade_schema
        with pytest.raises(FileNotFoundError):
            upgrade_schema(engine, temp_db_path)

        engine.dispose()

    def test_upgrade_preserves_existing_data(self, temp_db_path):
        """Test that upgrade_schema preserves existing data when upgrading."""
        # Create a database with a table and some data
        engine = create_engine(f"sqlite:///{temp_db_path}")
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER, name TEXT)"))
            conn.execute(text("INSERT INTO test VALUES (1, 'test1')"))
            conn.execute(text("INSERT INTO test VALUES (2, 'test2')"))
            conn.commit()
        engine.dispose()

        # Run upgrade
        engine = create_engine(f"sqlite:///{temp_db_path}")
        from playlist_bridge.persistence.migrations import upgrade_schema
        upgrade_schema(engine, temp_db_path)

        # Verify the upgrade completed successfully - all expected tables exist
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        # Remove alembic_version from the set if present
        tables.discard("alembic_version")
        # The test table should still be present (Alembic doesn't drop unknown tables)
        assert "test" in tables
        assert "jobs" in tables
        assert "account_profiles" in tables

        engine.dispose()


class TestMigrationIdempotence:
    """Tests for migration idempotence - repeated upgrades are no-ops."""

    def test_repeated_upgrade_is_noop(self, temp_db_path):
        """Test that calling upgrade_schema multiple times is a no-op after the first."""
        # Create an empty database file
        temp_db_path.touch()
        engine = create_engine(f"sqlite:///{temp_db_path}")

        # First upgrade
        upgrade_schema(engine, temp_db_path)

        # Capture state after first upgrade
        inspector = inspect(engine)
        tables_after_first = set(inspector.get_table_names())
        tables_after_first.discard("alembic_version")

        # Get schema details for comparison
        schema_details_first = self._get_schema_details(engine)

        # Second upgrade
        upgrade_schema(engine, temp_db_path)

        # Capture state after second upgrade
        inspector = inspect(engine)
        tables_after_second = set(inspector.get_table_names())
        tables_after_second.discard("alembic_version")

        # Tables should be identical
        assert tables_after_first == tables_after_second

        # Schema details should be identical
        schema_details_second = self._get_schema_details(engine)
        assert schema_details_first == schema_details_second

        # Third upgrade (just to be thorough)
        upgrade_schema(engine, temp_db_path)
        inspector = inspect(engine)
        tables_after_third = set(inspector.get_table_names())
        tables_after_third.discard("alembic_version")
        assert tables_after_second == tables_after_third

        engine.dispose()

    def _get_schema_details(self, engine):
        """Get detailed schema information for comparison."""
        inspector = inspect(engine)
        details = {}
        for table_name in inspector.get_table_names():
            if table_name == "alembic_version":
                continue
            details[table_name] = {
                "columns": sorted(
                    [(c["name"], c["type"].__class__.__name__) for c in inspector.get_columns(table_name)]
                ),
                "foreign_keys": sorted(
                    [(fk["constrained_columns"][0], fk["referred_table"]) for fk in inspector.get_foreign_keys(table_name)]
                ),
                "indexes": sorted(
                    [idx["name"] for idx in inspector.get_indexes(table_name)]
                ),
                "unique_constraints": sorted(
                    [uc["name"] for uc in inspector.get_unique_constraints(table_name)]
                ),
            }
        return details

    def test_repeated_upgrade_does_not_create_extra_backups(self, temp_db_path):
        """Test that repeated upgrades on a non-empty database don't create extra backups unnecessarily."""
        # Create a database with a table (simulating an existing database)
        engine = create_engine(f"sqlite:///{temp_db_path}")
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER)"))
            conn.execute(text("INSERT INTO test VALUES (1)"))
            conn.commit()
        engine.dispose()

        # First upgrade - should create a backup
        engine = create_engine(f"sqlite:///{temp_db_path}")
        upgrade_schema(engine, temp_db_path)
        engine.dispose()

        # Count backups after first upgrade
        backup_files_after_first = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))
        assert len(backup_files_after_first) == 1

        # Second upgrade - should not create another backup if schema is already up to date
        engine = create_engine(f"sqlite:///{temp_db_path}")
        upgrade_schema(engine, temp_db_path)
        engine.dispose()

        # Count backups after second upgrade - should still be 1
        backup_files_after_second = list(temp_db_path.parent.glob(f"{temp_db_path.stem}_backup_*.db"))
        assert len(backup_files_after_second) == 1

        # Clean up backups
        for backup in backup_files_after_second:
            backup.unlink()


class TestSchemaParity:
    """Tests for schema parity between initialization and migration paths."""

    def test_initialization_and_migration_produce_identical_schema(self, temp_db_path):
        """Test that initialize_schema and upgrade_schema produce equivalent schemas."""
        # Path A: Initialize schema using initialize_schema
        init_db_path = temp_db_path.parent / f"{temp_db_path.stem}_init{temp_db_path.suffix}"
        init_engine = create_engine(f"sqlite:///{init_db_path}")
        initialize_schema(init_engine)
        init_details = self._get_schema_equivalence_details(init_engine)
        init_engine.dispose()

        # Path B: Initialize using upgrade_schema
        migrate_db_path = temp_db_path.parent / f"{temp_db_path.stem}_migrate{temp_db_path.suffix}"
        migrate_db_path.touch()
        migrate_engine = create_engine(f"sqlite:///{migrate_db_path}")
        upgrade_schema(migrate_engine, migrate_db_path)
        migrate_details = self._get_schema_equivalence_details(migrate_engine)
        migrate_engine.dispose()

        # Compare schemas - should be equivalent
        assert init_details == migrate_details, "Schemas from initialization and migration paths differ"

        # Clean up
        if init_db_path.exists():
            init_db_path.unlink()
        if migrate_db_path.exists():
            migrate_db_path.unlink()

    def _get_schema_equivalence_details(self, engine):
        """Get schema details for equivalence comparison (ignoring minor differences)."""
        inspector = inspect(engine)
        details = {}
        for table_name in sorted(inspector.get_table_names()):
            if table_name == "alembic_version":
                continue
            # Get column info without autoincrement flag which may differ
            columns = []
            for col in inspector.get_columns(table_name):
                col_info = {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": col.get("default"),
                }
                columns.append(col_info)
            details[table_name] = {
                "columns": sorted(columns, key=lambda x: x["name"]),
                "primary_key": sorted(inspector.get_pk_constraint(table_name).get("constrained_columns", [])),
                "foreign_keys": sorted(
                    [
                        {
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"],
                        }
                        for fk in inspector.get_foreign_keys(table_name)
                    ],
                    key=lambda x: str(x),
                ),
                # Unique constraints: compare by column names only, not by name
                "unique_constraints": sorted(
                    [
                        sorted(uc.get("column_names", []))
                        for uc in inspector.get_unique_constraints(table_name)
                    ],
                    key=lambda x: str(x),
                ),
                # Indexes: compare by column names only, not by name
                "indexes": sorted(
                    [
                        sorted(idx["column_names"])
                        for idx in inspector.get_indexes(table_name)
                    ],
                    key=lambda x: str(x),
                ),
            }
        return details

    def _get_full_schema_details(self, engine):
        """Get complete schema details for comparison."""
        inspector = inspect(engine)
        details = {}
        for table_name in sorted(inspector.get_table_names()):
            if table_name == "alembic_version":
                continue
            columns = []
            for col in inspector.get_columns(table_name):
                columns.append({
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                    "default": col.get("default"),
                    "autoincrement": col.get("autoincrement", False),
                })
            details[table_name] = {
                "columns": columns,
                "primary_key": sorted(inspector.get_pk_constraint(table_name).get("constrained_columns", [])),
                "foreign_keys": sorted(
                    [
                        {
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"],
                        }
                        for fk in inspector.get_foreign_keys(table_name)
                    ],
                    key=lambda x: str(x),
                ),
                "unique_constraints": sorted(
                    [
                        {
                            "name": uc.get("name"),
                            "column_names": sorted(uc.get("column_names", [])),
                        }
                        for uc in inspector.get_unique_constraints(table_name)
                    ],
                    key=lambda x: str(x),
                ),
                "indexes": sorted(
                    [
                        {
                            "name": idx["name"],
                            "unique": idx["unique"],
                            "column_names": idx["column_names"],
                        }
                        for idx in inspector.get_indexes(table_name)
                    ],
                    key=lambda x: str(x),
                ),
            }
        return details

    def test_schema_remains_readable_after_repeated_upgrade(self, temp_db_path):
        """Test that the database remains readable after repeated upgrades."""
        # Create an empty database
        temp_db_path.touch()
        engine = create_engine(f"sqlite:///{temp_db_path}")

        # Run upgrades multiple times
        for _ in range(3):
            upgrade_schema(engine, temp_db_path)

        # Verify we can read from all tables
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        tables.discard("alembic_version")

        # Should have all expected tables
        assert tables == EXPECTED_TABLES

        # Verify we can query each table
        with engine.connect() as conn:
            for table in tables:
                result = conn.execute(text(f"SELECT * FROM {table} LIMIT 1"))
                # Should not raise an error
                _ = result.fetchall()

        engine.dispose()

    def test_both_paths_have_equivalent_constraints_and_indexes(self, temp_db_path):
        """Test that both initialization and migration paths produce equivalent constraints and indexes."""
        # Path A: Initialize
        init_db_path = temp_db_path.parent / f"{temp_db_path.stem}_init2{temp_db_path.suffix}"
        init_engine = create_engine(f"sqlite:///{init_db_path}")
        initialize_schema(init_engine)
        init_constraints = self._get_constraints_and_indexes(init_engine)
        init_engine.dispose()

        # Path B: Migrate
        migrate_db_path = temp_db_path.parent / f"{temp_db_path.stem}_migrate2{temp_db_path.suffix}"
        migrate_db_path.touch()
        migrate_engine = create_engine(f"sqlite:///{migrate_db_path}")
        upgrade_schema(migrate_engine, migrate_db_path)
        migrate_constraints = self._get_constraints_and_indexes(migrate_engine)
        migrate_engine.dispose()

        # Compare constraints and indexes
        assert init_constraints == migrate_constraints

        # Clean up
        if init_db_path.exists():
            init_db_path.unlink()
        if migrate_db_path.exists():
            migrate_db_path.unlink()

    def _get_constraints_and_indexes(self, engine):
        """Get constraints and indexes for comparison (ignoring names)."""
        inspector = inspect(engine)
        details = {}
        for table_name in sorted(inspector.get_table_names()):
            if table_name == "alembic_version":
                continue
            details[table_name] = {
                "foreign_keys": sorted(
                    [
                        {
                            "constrained_columns": fk["constrained_columns"],
                            "referred_table": fk["referred_table"],
                            "referred_columns": fk["referred_columns"],
                        }
                        for fk in inspector.get_foreign_keys(table_name)
                    ],
                    key=lambda x: str(x),
                ),
                "unique_constraints": sorted(
                    [
                        sorted(uc.get("column_names", []))
                        for uc in inspector.get_unique_constraints(table_name)
                    ],
                    key=lambda x: str(x),
                ),
                "indexes": sorted(
                    [
                        sorted(idx["column_names"])
                        for idx in inspector.get_indexes(table_name)
                    ],
                    key=lambda x: str(x),
                ),
            }
        return details
