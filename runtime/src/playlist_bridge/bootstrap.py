"""Production composition root for playlist-bridge.

This module provides the production application state and dependency builders
for auth, job queries, and review repositories. It is the only CLI path to
database, keychain, and provider construction.
"""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from playlist_bridge.credentials.store import KeyringCacheHandler
from playlist_bridge.domain.enums import DestinationService, SourceService
from playlist_bridge.persistence import Base, create_engine_for_path, upgrade_schema
from playlist_bridge.persistence.repositories import (
    SqlAlchemyMatchCacheRepository,
    SqlAlchemyMatchDecisionRepository,
    SqlAlchemyManualCorrectionRepository,
)
from playlist_bridge.ports import (
    AccountProfileRepository,
    CredentialStore,
    JobRepository,
    MatchCacheRepository,
    MatchDecisionRepository,
    ManualCorrectionRepository,
    ReviewRepositories,
    SourceTrackRepository,
)
from playlist_bridge.paths import ensure_app_directories


# ============================================================================
# Application State
# ============================================================================


class ApplicationState:
    """Immutable typed bundle of application state.

    Aggregates the engine, session factory, credential store, and all repository
    ports required by auth, matching, review, and runner code.

    Attributes:
        engine: SQLAlchemy Engine instance for database connections.
        session_factory: SQLAlchemy sessionmaker for creating Session objects.
        credentials: CredentialStore instance for OAuth token management.
        profiles: AccountProfileRepository instance for profile persistence.
        jobs: JobRepository instance for job persistence and leases.
        tracks: SourceTrackRepository instance for source track persistence.
        decisions: MatchDecisionRepository instance for match decision persistence.
        match_cache: MatchCacheRepository instance for match cache persistence.
        corrections: ManualCorrectionRepository instance for correction persistence.
    """

    def __init__(
        self,
        engine: Engine,
        session_factory: sessionmaker[Session],
        credentials: CredentialStore,
        profiles: AccountProfileRepository,
        jobs: JobRepository,
        tracks: SourceTrackRepository,
        decisions: MatchDecisionRepository,
        match_cache: MatchCacheRepository,
        corrections: ManualCorrectionRepository,
    ) -> None:
        """Initialize the application state.

        Args:
            engine: SQLAlchemy Engine instance.
            session_factory: SQLAlchemy sessionmaker for creating Session objects.
            credentials: CredentialStore instance for OAuth token management.
            profiles: AccountProfileRepository instance for profile persistence.
            jobs: JobRepository instance for job persistence and leases.
            tracks: SourceTrackRepository instance for source track persistence.
            decisions: MatchDecisionRepository instance for match decision persistence.
            match_cache: MatchCacheRepository instance for match cache persistence.
            corrections: ManualCorrectionRepository instance for correction persistence.

        Raises:
            ValueError: If any of the arguments are None.
        """
        if engine is None:
            raise ValueError("engine cannot be None")
        if session_factory is None:
            raise ValueError("session_factory cannot be None")
        if credentials is None:
            raise ValueError("credentials cannot be None")
        if profiles is None:
            raise ValueError("profiles cannot be None")
        if jobs is None:
            raise ValueError("jobs cannot be None")
        if tracks is None:
            raise ValueError("tracks cannot be None")
        if decisions is None:
            raise ValueError("decisions cannot be None")
        if match_cache is None:
            raise ValueError("match_cache cannot be None")
        if corrections is None:
            raise ValueError("corrections cannot be None")

        self.engine = engine
        self.session_factory = session_factory
        self.credentials = credentials
        self.profiles = profiles
        self.jobs = jobs
        self.tracks = tracks
        self.decisions = decisions
        self.match_cache = match_cache
        self.corrections = corrections


# ============================================================================
# Auth Dependencies
# ============================================================================


class AuthDependencies:
    """Dependency container for authentication commands.

    Aggregates the profile repository and credential store needed by auth commands.

    Attributes:
        profiles: AccountProfileRepository instance for profile persistence.
        credentials: CredentialStore instance for OAuth token management.
    """

    def __init__(
        self,
        profiles: AccountProfileRepository,
        credentials: CredentialStore,
    ) -> None:
        """Initialize the auth dependencies container.

        Args:
            profiles: AccountProfileRepository instance for profile persistence.
            credentials: CredentialStore instance for OAuth token management.

        Raises:
            ValueError: If any of the arguments are None.
        """
        if profiles is None:
            raise ValueError("profiles repository cannot be None")
        if credentials is None:
            raise ValueError("credentials store cannot be None")
        self.profiles = profiles
        self.credentials = credentials


# ============================================================================
# Job Query Dependencies
# ============================================================================


class JobQueryDependencies:
    """Dependency container for job query commands.

    Aggregates the job repository needed by job query commands.

    Attributes:
        jobs: JobRepository instance for job persistence and leases.
    """

    def __init__(self, jobs: JobRepository) -> None:
        """Initialize the job query dependencies container.

        Args:
            jobs: JobRepository instance for job persistence and leases.

        Raises:
            ValueError: If jobs is None.
        """
        if jobs is None:
            raise ValueError("jobs repository cannot be None")
        self.jobs = jobs


# ============================================================================
# Production Builders
# ============================================================================


def initialize_application_state(
    *,
    database_file: Path | None = None,
    keyring_backend: Any | None = None,
) -> ApplicationState:
    """Initialize the production application state.

    This function creates application directories, opens the selected SQLite
    database, runs backup-protected migrations, constructs the keyring adapter,
    and every SQLAlchemy repository adapter.

    Args:
        database_file: Path to the SQLite database file. If None, uses the
            default path from paths.database_path().
        keyring_backend: Optional keyring backend to use. If None, uses the
            default keyring backend.

    Returns:
        ApplicationState: The initialized application state.

    Raises:
        OSError: If directory creation fails.
        SQLAlchemyError: If database operations fail.
        MigrationError: If schema migration fails.
        KeyringError: If keyring operations fail.

    Side Effects:
        filesystem_directory_create: Creates application directories.
        sqlite_open: Opens the SQLite database.
        sqlite_migration: Upgrades the schema to the latest version.
        database_backup: Creates a backup before migration.
    """
    from playlist_bridge.paths import database_path as default_db_path

    # Create application directories
    ensure_app_directories()

    # Determine database file path
    db_path = database_file if database_file is not None else default_db_path()

    # Create engine and upgrade schema
    engine = create_engine_for_path(db_path)
    upgrade_schema(engine)

    # Create session factory
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # Create credential store
    # Note: keyring_backend is passed through but not directly used here
    # as KeyringCacheHandler uses the default keyring backend
    credentials = KeyringCacheHandler()

    # Create repository adapters
    # Note: For JobRepository, SourceTrackRepository, and AccountProfileRepository,
    # the concrete implementations are not yet available as adapter classes.
    # We use the function-based implementations from persistence.repositories.
    # This is a placeholder - the actual implementations will be provided
    # by the repository adapters in a future dispatch.
    # For now, we raise NotImplementedError for the missing repository adapters.
    # This will be completed when the repository adapters are implemented.
    raise NotImplementedError(
        "Repository adapters for JobRepository, SourceTrackRepository, "
        "and AccountProfileRepository are not yet implemented. "
        "This will be completed in a future dispatch."
    )


def build_auth_dependencies(
    state: ApplicationState | None = None,
) -> AuthDependencies:
    """Build authentication dependencies from application state.

    Args:
        state: ApplicationState instance. If None, initializes a new state.

    Returns:
        AuthDependencies: Container with profiles and credentials repositories.

    Raises:
        OSError: If directory creation fails.
        SQLAlchemyError: If database operations fail.
        MigrationError: If schema migration fails.
        KeyringError: If keyring operations fail.

    Side Effects:
        filesystem_directory_create: Creates application directories.
        sqlite_open: Opens the SQLite database.
        sqlite_migration: Upgrades the schema to the latest version.
    """
    if state is None:
        state = initialize_application_state()

    return AuthDependencies(
        profiles=state.profiles,
        credentials=state.credentials,
    )


def build_job_query_dependencies(
    state: ApplicationState | None = None,
) -> JobQueryDependencies:
    """Build job query dependencies from application state.

    Args:
        state: ApplicationState instance. If None, initializes a new state.

    Returns:
        JobQueryDependencies: Container with job repository.

    Raises:
        OSError: If directory creation fails.
        SQLAlchemyError: If database operations fail.
        MigrationError: If schema migration fails.
        KeyringError: If keyring operations fail.

    Side Effects:
        filesystem_directory_create: Creates application directories.
        sqlite_open: Opens the SQLite database.
        sqlite_migration: Upgrades the schema to the latest version.
    """
    if state is None:
        state = initialize_application_state()

    return JobQueryDependencies(jobs=state.jobs)


def build_review_dependencies(
    state: ApplicationState | None = None,
) -> ReviewRepositories:
    """Build review repositories from application state.

    Args:
        state: ApplicationState instance. If None, initializes a new state.

    Returns:
        ReviewRepositories: Container with jobs, tracks, decisions, and corrections.

    Raises:
        OSError: If directory creation fails.
        SQLAlchemyError: If database operations fail.
        MigrationError: If schema migration fails.
        KeyringError: If keyring operations fail.

    Side Effects:
        filesystem_directory_create: Creates application directories.
        sqlite_open: Opens the SQLite database.
        sqlite_migration: Upgrades the schema to the latest version.
    """
    if state is None:
        state = initialize_application_state()

    return ReviewRepositories(
        jobs=state.jobs,
        tracks=state.tracks,
        decisions=state.decisions,
        corrections=state.corrections,
    )
