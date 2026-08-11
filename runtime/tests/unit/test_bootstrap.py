"""Unit tests for the bootstrap module."""

import pytest
from unittest.mock import MagicMock, patch

from playlist_bridge.bootstrap import (
    ApplicationState,
    AuthDependencies,
    JobQueryDependencies,
    build_auth_dependencies,
    build_job_query_dependencies,
    build_review_dependencies,
    initialize_application_state,
)
from playlist_bridge.ports import ReviewRepositories


class TestApplicationState:
    """Tests for the ApplicationState class."""

    def test_initialization_with_all_dependencies(self):
        """Test that ApplicationState initializes correctly with all dependencies."""
        # Create mock dependencies
        mock_engine = MagicMock()
        mock_session_factory = MagicMock()
        mock_credentials = MagicMock()
        mock_profiles = MagicMock()
        mock_jobs = MagicMock()
        mock_tracks = MagicMock()
        mock_decisions = MagicMock()
        mock_match_cache = MagicMock()
        mock_corrections = MagicMock()

        # Initialize ApplicationState
        state = ApplicationState(
            engine=mock_engine,
            session_factory=mock_session_factory,
            credentials=mock_credentials,
            profiles=mock_profiles,
            jobs=mock_jobs,
            tracks=mock_tracks,
            decisions=mock_decisions,
            match_cache=mock_match_cache,
            corrections=mock_corrections,
        )

        # Verify attributes are set correctly
        assert state.engine is mock_engine
        assert state.session_factory is mock_session_factory
        assert state.credentials is mock_credentials
        assert state.profiles is mock_profiles
        assert state.jobs is mock_jobs
        assert state.tracks is mock_tracks
        assert state.decisions is mock_decisions
        assert state.match_cache is mock_match_cache
        assert state.corrections is mock_corrections

    def test_initialization_raises_value_error_for_none_engine(self):
        """Test that ValueError is raised when engine is None."""
        with pytest.raises(ValueError, match="engine cannot be None"):
            ApplicationState(
                engine=None,
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_session_factory(self):
        """Test that ValueError is raised when session_factory is None."""
        with pytest.raises(ValueError, match="session_factory cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=None,
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_credentials(self):
        """Test that ValueError is raised when credentials is None."""
        with pytest.raises(ValueError, match="credentials cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=None,
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_profiles(self):
        """Test that ValueError is raised when profiles is None."""
        with pytest.raises(ValueError, match="profiles cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=None,
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_jobs(self):
        """Test that ValueError is raised when jobs is None."""
        with pytest.raises(ValueError, match="jobs cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=None,
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_tracks(self):
        """Test that ValueError is raised when tracks is None."""
        with pytest.raises(ValueError, match="tracks cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=None,
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_decisions(self):
        """Test that ValueError is raised when decisions is None."""
        with pytest.raises(ValueError, match="decisions cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=None,
                match_cache=MagicMock(),
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_match_cache(self):
        """Test that ValueError is raised when match_cache is None."""
        with pytest.raises(ValueError, match="match_cache cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=None,
                corrections=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_corrections(self):
        """Test that ValueError is raised when corrections is None."""
        with pytest.raises(ValueError, match="corrections cannot be None"):
            ApplicationState(
                engine=MagicMock(),
                session_factory=MagicMock(),
                credentials=MagicMock(),
                profiles=MagicMock(),
                jobs=MagicMock(),
                tracks=MagicMock(),
                decisions=MagicMock(),
                match_cache=MagicMock(),
                corrections=None,
            )


class TestAuthDependencies:
    """Tests for the AuthDependencies class."""

    def test_initialization_with_all_dependencies(self):
        """Test that AuthDependencies initializes correctly with all dependencies."""
        mock_profiles = MagicMock()
        mock_credentials = MagicMock()

        auth_deps = AuthDependencies(
            profiles=mock_profiles,
            credentials=mock_credentials,
        )

        assert auth_deps.profiles is mock_profiles
        assert auth_deps.credentials is mock_credentials

    def test_initialization_raises_value_error_for_none_profiles(self):
        """Test that ValueError is raised when profiles is None."""
        with pytest.raises(ValueError, match="profiles repository cannot be None"):
            AuthDependencies(
                profiles=None,
                credentials=MagicMock(),
            )

    def test_initialization_raises_value_error_for_none_credentials(self):
        """Test that ValueError is raised when credentials is None."""
        with pytest.raises(ValueError, match="credentials store cannot be None"):
            AuthDependencies(
                profiles=MagicMock(),
                credentials=None,
            )


class TestJobQueryDependencies:
    """Tests for the JobQueryDependencies class."""

    def test_initialization_with_job_repository(self):
        """Test that JobQueryDependencies initializes correctly with job repository."""
        mock_jobs = MagicMock()

        job_query_deps = JobQueryDependencies(jobs=mock_jobs)

        assert job_query_deps.jobs is mock_jobs

    def test_initialization_raises_value_error_for_none_jobs(self):
        """Test that ValueError is raised when jobs is None."""
        with pytest.raises(ValueError, match="jobs repository cannot be None"):
            JobQueryDependencies(jobs=None)


class TestInitializeApplicationState:
    """Tests for the initialize_application_state function."""

    @patch("playlist_bridge.bootstrap.ensure_app_directories")
    @patch("playlist_bridge.bootstrap.create_engine_for_path")
    @patch("playlist_bridge.bootstrap.upgrade_schema")
    @patch("playlist_bridge.bootstrap.KeyringCacheHandler")
    @patch("playlist_bridge.bootstrap.sessionmaker")
    def test_initialize_application_state_raises_not_implemented(
        self,
        mock_sessionmaker,
        mock_keyring_handler,
        mock_upgrade_schema,
        mock_create_engine,
        mock_ensure_dirs,
    ):
        """Test that initialize_application_state raises NotImplementedError."""
        # Setup mocks
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_session_factory = MagicMock()
        mock_sessionmaker.return_value = mock_session_factory
        mock_keyring_handler.return_value = MagicMock()

        # Call and expect NotImplementedError
        with pytest.raises(
            NotImplementedError,
            match="Repository adapters for JobRepository, SourceTrackRepository",
        ):
            initialize_application_state()

        # Verify that setup functions were called
        mock_ensure_dirs.assert_called_once()
        mock_create_engine.assert_called_once()
        mock_upgrade_schema.assert_called_once_with(mock_engine)
        mock_keyring_handler.assert_called_once()
        mock_sessionmaker.assert_called_once_with(
            bind=mock_engine,
            autocommit=False,
            autoflush=False,
        )


class TestBuildAuthDependencies:
    """Tests for the build_auth_dependencies function."""

    @patch("playlist_bridge.bootstrap.initialize_application_state")
    def test_build_auth_dependencies_with_state(self, mock_initialize):
        """Test that build_auth_dependencies uses provided state."""
        # Create mock state
        mock_state = MagicMock()
        mock_state.profiles = MagicMock()
        mock_state.credentials = MagicMock()

        # Call function with state
        result = build_auth_dependencies(state=mock_state)

        # Verify initialize_application_state was NOT called
        mock_initialize.assert_not_called()

        # Verify result is AuthDependencies with correct attributes
        assert isinstance(result, AuthDependencies)
        assert result.profiles is mock_state.profiles
        assert result.credentials is mock_state.credentials

    @patch("playlist_bridge.bootstrap.initialize_application_state")
    def test_build_auth_dependencies_without_state(self, mock_initialize):
        """Test that build_auth_dependencies initializes state when not provided."""
        # Create mock state
        mock_state = MagicMock()
        mock_state.profiles = MagicMock()
        mock_state.credentials = MagicMock()
        mock_initialize.return_value = mock_state

        # Call function without state
        result = build_auth_dependencies()

        # Verify initialize_application_state was called
        mock_initialize.assert_called_once()

        # Verify result is AuthDependencies with correct attributes
        assert isinstance(result, AuthDependencies)
        assert result.profiles is mock_state.profiles
        assert result.credentials is mock_state.credentials


class TestBuildJobQueryDependencies:
    """Tests for the build_job_query_dependencies function."""

    @patch("playlist_bridge.bootstrap.initialize_application_state")
    def test_build_job_query_dependencies_with_state(self, mock_initialize):
        """Test that build_job_query_dependencies uses provided state."""
        # Create mock state
        mock_state = MagicMock()
        mock_state.jobs = MagicMock()

        # Call function with state
        result = build_job_query_dependencies(state=mock_state)

        # Verify initialize_application_state was NOT called
        mock_initialize.assert_not_called()

        # Verify result is JobQueryDependencies with correct attributes
        assert isinstance(result, JobQueryDependencies)
        assert result.jobs is mock_state.jobs

    @patch("playlist_bridge.bootstrap.initialize_application_state")
    def test_build_job_query_dependencies_without_state(self, mock_initialize):
        """Test that build_job_query_dependencies initializes state when not provided."""
        # Create mock state
        mock_state = MagicMock()
        mock_state.jobs = MagicMock()
        mock_initialize.return_value = mock_state

        # Call function without state
        result = build_job_query_dependencies()

        # Verify initialize_application_state was called
        mock_initialize.assert_called_once()

        # Verify result is JobQueryDependencies with correct attributes
        assert isinstance(result, JobQueryDependencies)
        assert result.jobs is mock_state.jobs


class TestBuildReviewDependencies:
    """Tests for the build_review_dependencies function."""

    @patch("playlist_bridge.bootstrap.initialize_application_state")
    def test_build_review_dependencies_with_state(self, mock_initialize):
        """Test that build_review_dependencies uses provided state."""
        # Create mock state
        mock_state = MagicMock()
        mock_state.jobs = MagicMock()
        mock_state.tracks = MagicMock()
        mock_state.decisions = MagicMock()
        mock_state.corrections = MagicMock()

        # Call function with state
        result = build_review_dependencies(state=mock_state)

        # Verify initialize_application_state was NOT called
        mock_initialize.assert_not_called()

        # Verify result is ReviewRepositories with correct attributes
        assert isinstance(result, ReviewRepositories)
        assert result.jobs is mock_state.jobs
        assert result.tracks is mock_state.tracks
        assert result.decisions is mock_state.decisions
        assert result.corrections is mock_state.corrections

    @patch("playlist_bridge.bootstrap.initialize_application_state")
    def test_build_review_dependencies_without_state(self, mock_initialize):
        """Test that build_review_dependencies initializes state when not provided."""
        # Create mock state
        mock_state = MagicMock()
        mock_state.jobs = MagicMock()
        mock_state.tracks = MagicMock()
        mock_state.decisions = MagicMock()
        mock_state.corrections = MagicMock()
        mock_initialize.return_value = mock_state

        # Call function without state
        result = build_review_dependencies()

        # Verify initialize_application_state was called
        mock_initialize.assert_called_once()

        # Verify result is ReviewRepositories with correct attributes
        assert isinstance(result, ReviewRepositories)
        assert result.jobs is mock_state.jobs
        assert result.tracks is mock_state.tracks
        assert result.decisions is mock_state.decisions
        assert result.corrections is mock_state.corrections
