"""Unit tests for credential and profile ports."""

import pytest
from typing import Any, Mapping

from playlist_bridge.domain.enums import DestinationService, SourceService
from playlist_bridge.ports import (
    CredentialCorruptionError,
    CredentialStore,
    AccountProfileRepository,
    IntegrityError,
    KeyringError,
)


# ============================================================================
# Fake implementations for testing the protocols
# ============================================================================


class InMemoryCredentialStore:
    """In-memory fake implementation of CredentialStore for testing."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], dict[str, Any]] = {}

    def save(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
        token_payload: Mapping[str, Any],
    ) -> None:
        """Save credentials to the in-memory store."""
        # Validate serializability
        if not isinstance(token_payload, dict):
            raise CredentialCorruptionError(
                service=str(service),
                profile_name=profile_name,
                safe_message="token_payload must be a dict",
            )
        # Convert to dict for storage
        self._store[(str(service), profile_name)] = dict(token_payload)

    def load(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
    ) -> dict[str, Any] | None:
        """Load credentials from the in-memory store."""
        key = (str(service), profile_name)
        if key not in self._store:
            return None
        # Simulate corruption check
        data = self._store[key]
        if not isinstance(data, dict):
            raise CredentialCorruptionError(
                service=str(service),
                profile_name=profile_name,
                safe_message="stored data is not a dict",
            )
        return dict(data)

    def delete(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
    ) -> bool:
        """Delete credentials from the in-memory store."""
        key = (str(service), profile_name)
        if key not in self._store:
            return False
        del self._store[key]
        return True


class FakeAccountProfile:
    """Fake AccountProfile for testing the repository protocol."""

    def __init__(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
        account_id: str,
        display_name: str,
    ) -> None:
        self.service = service
        self.profile_name = profile_name
        self.account_id = account_id
        self.display_name = display_name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FakeAccountProfile):
            return False
        return (
            self.service == other.service
            and self.profile_name == other.profile_name
            and self.account_id == other.account_id
            and self.display_name == other.display_name
        )

    def __repr__(self) -> str:
        return (
            f"FakeAccountProfile(service={self.service!r}, "
            f"profile_name={self.profile_name!r}, "
            f"account_id={self.account_id!r}, "
            f"display_name={self.display_name!r})"
        )


class InMemoryAccountProfileRepository:
    """In-memory fake implementation of AccountProfileRepository for testing."""

    def __init__(self) -> None:
        self._profiles: dict[tuple[str, str], FakeAccountProfile] = {}

    def save(self, profile: FakeAccountProfile) -> FakeAccountProfile:
        """Save a profile to the in-memory repository."""
        key = (str(profile.service), profile.profile_name)
        if key in self._profiles:
            # Simulate integrity error on duplicate
            raise IntegrityError(
                f"Profile {profile.profile_name} for {profile.service} already exists"
            )
        self._profiles[key] = profile
        return profile

    def get(
        self,
        service: SourceService | DestinationService,
        profile_name: str,
    ) -> FakeAccountProfile | None:
        """Get a profile by service and profile name."""
        key = (str(service), profile_name)
        return self._profiles.get(key)

    def list(
        self,
        service: SourceService | DestinationService | None = None,
    ) -> list[FakeAccountProfile]:
        """List profiles, optionally filtered by service."""
        if service is None:
            return list(self._profiles.values())
        return [
            p
            for (svc, _), p in self._profiles.items()
            if svc == str(service)
        ]


# ============================================================================
# Tests for CredentialStore protocol
# ============================================================================


class TestCredentialStore:
    """Test that CredentialStore protocol is satisfied by fake implementation."""

    def test_fake_store_satisfies_protocol(self) -> None:
        """Verify that InMemoryCredentialStore satisfies the CredentialStore protocol."""
        store: CredentialStore = InMemoryCredentialStore()
        assert isinstance(store, CredentialStore)

    def test_save_and_load_round_trip(self) -> None:
        """Test save and load round trip with valid data."""
        store = InMemoryCredentialStore()
        service = SourceService.YOUTUBE
        profile_name = "default"
        token_payload = {"access_token": "token123", "refresh_token": "refresh456"}

        store.save(service, profile_name, token_payload)
        loaded = store.load(service, profile_name)

        assert loaded is not None
        assert loaded["access_token"] == "token123"
        assert loaded["refresh_token"] == "refresh456"

    def test_load_missing_returns_none(self) -> None:
        """Test load returns None for non-existent credentials."""
        store = InMemoryCredentialStore()
        result = store.load(SourceService.YOUTUBE, "nonexistent")
        assert result is None

    def test_delete_returns_true_when_exists(self) -> None:
        """Test delete returns True when credentials existed."""
        store = InMemoryCredentialStore()
        service = SourceService.YOUTUBE
        profile_name = "default"
        store.save(service, profile_name, {"token": "value"})

        deleted = store.delete(service, profile_name)
        assert deleted is True
        assert store.load(service, profile_name) is None

    def test_delete_returns_false_when_missing(self) -> None:
        """Test delete returns False when credentials did not exist."""
        store = InMemoryCredentialStore()
        deleted = store.delete(SourceService.YOUTUBE, "nonexistent")
        assert deleted is False

    def test_save_raises_credential_corruption_error(self) -> None:
        """Test save raises CredentialCorruptionError for invalid payload."""
        store = InMemoryCredentialStore()

        # The fake store only validates that token_payload is a dict
        # We need to force an error by passing something that raises
        with pytest.raises(CredentialCorruptionError) as exc:
            # Pass a non-dict to trigger the validation
            store.save(
                SourceService.YOUTUBE,
                "default",
                "not_a_dict",  # type: ignore[arg-type]
            )
        assert "token_payload must be a dict" in str(exc.value)
        assert exc.value.service == "SourceService.YOUTUBE"
        assert exc.value.profile_name == "default"

    def test_load_raises_credential_corruption_error(self) -> None:
        """Test load raises CredentialCorruptionError for corrupted data."""
        store = InMemoryCredentialStore()
        service = SourceService.YOUTUBE
        profile_name = "default"

        # Manually corrupt the store
        store._store[(str(service), profile_name)] = "corrupted"  # type: ignore[assignment]

        with pytest.raises(CredentialCorruptionError) as exc:
            store.load(service, profile_name)
        assert "stored data is not a dict" in str(exc.value)
        assert exc.value.service == "SourceService.YOUTUBE"
        assert exc.value.profile_name == "default"


# ============================================================================
# Tests for AccountProfileRepository protocol
# ============================================================================


class TestAccountProfileRepository:
    """Test that AccountProfileRepository protocol is satisfied by fake implementation."""

    def test_fake_repository_satisfies_protocol(self) -> None:
        """Verify that InMemoryAccountProfileRepository satisfies the protocol."""
        repo: AccountProfileRepository = InMemoryAccountProfileRepository()
        assert isinstance(repo, AccountProfileRepository)

    def test_save_and_get_round_trip(self) -> None:
        """Test save and get round trip with valid data."""
        repo = InMemoryAccountProfileRepository()
        profile = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )

        saved = repo.save(profile)
        loaded = repo.get(SourceService.YOUTUBE, "default")

        assert loaded is not None
        assert loaded == saved
        assert loaded.profile_name == "default"
        assert loaded.account_id == "channel123"
        assert loaded.display_name == "My YouTube Channel"

    def test_get_missing_returns_none(self) -> None:
        """Test get returns None for non-existent profile."""
        repo = InMemoryAccountProfileRepository()
        result = repo.get(SourceService.YOUTUBE, "nonexistent")
        assert result is None

    def test_save_raises_integrity_error_on_duplicate(self) -> None:
        """Test save raises IntegrityError for duplicate profiles."""
        repo = InMemoryAccountProfileRepository()
        profile = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )

        repo.save(profile)

        duplicate = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel456",
            display_name="Another Channel",
        )

        with pytest.raises(IntegrityError) as exc:
            repo.save(duplicate)
        assert "already exists" in str(exc.value)

    def test_list_all_profiles(self) -> None:
        """Test list returns all profiles when no service filter provided."""
        repo = InMemoryAccountProfileRepository()

        profile1 = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )
        profile2 = FakeAccountProfile(
            service=DestinationService.SPOTIFY,
            profile_name="work",
            account_id="user456",
            display_name="Work Spotify",
        )

        repo.save(profile1)
        repo.save(profile2)

        all_profiles = repo.list()
        assert len(all_profiles) == 2
        assert profile1 in all_profiles
        assert profile2 in all_profiles

    def test_list_filters_by_service(self) -> None:
        """Test list filters profiles by service."""
        repo = InMemoryAccountProfileRepository()

        profile1 = FakeAccountProfile(
            service=SourceService.YOUTUBE,
            profile_name="default",
            account_id="channel123",
            display_name="My YouTube Channel",
        )
        profile2 = FakeAccountProfile(
            service=DestinationService.SPOTIFY,
            profile_name="work",
            account_id="user456",
            display_name="Work Spotify",
        )

        repo.save(profile1)
        repo.save(profile2)

        youtube_profiles = repo.list(service=SourceService.YOUTUBE)
        assert len(youtube_profiles) == 1
        assert youtube_profiles[0] == profile1

        spotify_profiles = repo.list(service=DestinationService.SPOTIFY)
        assert len(spotify_profiles) == 1
        assert spotify_profiles[0] == profile2

    def test_list_returns_empty_when_none(self) -> None:
        """Test list returns empty list when no profiles match."""
        repo = InMemoryAccountProfileRepository()
        result = repo.list(service=SourceService.YOUTUBE)
        assert result == []


# ============================================================================
# Tests for error types
# ============================================================================


class TestErrorTypes:
    """Test that custom error types are properly defined."""

    def test_credential_corruption_error(self) -> None:
        """Test CredentialCorruptionError initialization."""
        err = CredentialCorruptionError(
            service="spotify",
            profile_name="default",
            safe_message="Token payload malformed",
        )
        assert err.service == "spotify"
        assert err.profile_name == "default"
        assert err.safe_message == "Token payload malformed"
        assert "spotify/default" in str(err)
        assert "Token payload malformed" in str(err)

    def test_keyring_error(self) -> None:
        """Test KeyringError initialization."""
        err = KeyringError("Keychain unlock failed")
        assert str(err) == "Keychain unlock failed"

    def test_integrity_error(self) -> None:
        """Test IntegrityError initialization."""
        err = IntegrityError("UNIQUE constraint failed")
        assert str(err) == "UNIQUE constraint failed"


# ============================================================================
# Tests for repository protocols
# ============================================================================


class TestRepositoryProtocols:
    """Test that repository protocols are properly defined."""

    def test_job_repository_protocol_exists(self) -> None:
        """Test that JobRepository protocol is defined."""
        from playlist_bridge.ports import JobRepository
        # Protocol should be a class that can be used for type checking
        assert isinstance(JobRepository, type)
        # Check that it's a Protocol subclass
        assert issubclass(JobRepository, Protocol)

    def test_source_track_repository_protocol_exists(self) -> None:
        """Test that SourceTrackRepository protocol is defined."""
        from playlist_bridge.ports import SourceTrackRepository
        assert isinstance(SourceTrackRepository, type)
        assert issubclass(SourceTrackRepository, Protocol)

    def test_match_decision_repository_protocol_exists(self) -> None:
        """Test that MatchDecisionRepository protocol is defined."""
        from playlist_bridge.ports import MatchDecisionRepository
        assert isinstance(MatchDecisionRepository, type)
        assert issubclass(MatchDecisionRepository, Protocol)

    def test_match_cache_repository_protocol_exists(self) -> None:
        """Test that MatchCacheRepository protocol is defined."""
        from playlist_bridge.ports import MatchCacheRepository
        assert isinstance(MatchCacheRepository, type)
        assert issubclass(MatchCacheRepository, Protocol)

    def test_manual_correction_repository_protocol_exists(self) -> None:
        """Test that ManualCorrectionRepository protocol is defined."""
        from playlist_bridge.ports import ManualCorrectionRepository
        assert isinstance(ManualCorrectionRepository, type)
        assert issubclass(ManualCorrectionRepository, Protocol)

    def test_clock_type_alias_exists(self) -> None:
        """Test that Clock type alias is defined."""
        from playlist_bridge.ports import Clock
        # Clock is a Callable[[], datetime]
        from typing import Callable
        from datetime import datetime
        assert isinstance(Clock, type) or Clock is Callable
        # Check that it's a callable type hint
        assert hasattr(Clock, "__origin__") or Clock is Callable

    def test_report_path_factory_type_alias_exists(self) -> None:
        """Test that ReportPathFactory type alias is defined."""
        from playlist_bridge.ports import ReportPathFactory
        from typing import Callable
        from pathlib import Path
        assert hasattr(ReportPathFactory, "__origin__") or ReportPathFactory is Callable


# ============================================================================
# Tests for dependency container classes
# ============================================================================


class TestRunnerRepositories:
    """Test RunnerRepositories dependency container."""

    def test_initialization_with_valid_repositories(self) -> None:
        """Test successful initialization with valid repositories."""
        from playlist_bridge.ports import (
            JobRepository,
            SourceTrackRepository,
            MatchDecisionRepository,
            RunnerRepositories,
        )

        # Create fake repository implementations
        class FakeJobRepository:
            pass

        class FakeTrackRepository:
            pass

        class FakeDecisionRepository:
            pass

        jobs = FakeJobRepository()
        tracks = FakeTrackRepository()
        decisions = FakeDecisionRepository()

        container = RunnerRepositories(
            jobs=jobs,  # type: ignore[arg-type]
            tracks=tracks,  # type: ignore[arg-type]
            decisions=decisions,  # type: ignore[arg-type]
        )

        assert container.jobs is jobs
        assert container.tracks is tracks
        assert container.decisions is decisions

    def test_initialization_raises_value_error_for_none_jobs(self) -> None:
        """Test that ValueError is raised when jobs is None."""
        from playlist_bridge.ports import (
            SourceTrackRepository,
            MatchDecisionRepository,
            RunnerRepositories,
        )

        with pytest.raises(ValueError, match="jobs repository cannot be None"):
            RunnerRepositories(
                jobs=None,  # type: ignore[arg-type]
                tracks=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_tracks(self) -> None:
        """Test that ValueError is raised when tracks is None."""
        from playlist_bridge.ports import (
            JobRepository,
            MatchDecisionRepository,
            RunnerRepositories,
        )

        with pytest.raises(ValueError, match="tracks repository cannot be None"):
            RunnerRepositories(
                jobs=None,  # type: ignore[arg-type]
                tracks=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_decisions(self) -> None:
        """Test that ValueError is raised when decisions is None."""
        from playlist_bridge.ports import (
            JobRepository,
            SourceTrackRepository,
            RunnerRepositories,
        )

        with pytest.raises(ValueError, match="decisions repository cannot be None"):
            RunnerRepositories(
                jobs=None,  # type: ignore[arg-type]
                tracks=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
            )


class TestReviewRepositories:
    """Test ReviewRepositories dependency container."""

    def test_initialization_with_valid_repositories(self) -> None:
        """Test successful initialization with valid repositories."""
        from playlist_bridge.ports import (
            JobRepository,
            SourceTrackRepository,
            MatchDecisionRepository,
            ManualCorrectionRepository,
            ReviewRepositories,
        )

        class FakeJobRepository:
            pass

        class FakeTrackRepository:
            pass

        class FakeDecisionRepository:
            pass

        class FakeCorrectionRepository:
            pass

        jobs = FakeJobRepository()
        tracks = FakeTrackRepository()
        decisions = FakeDecisionRepository()
        corrections = FakeCorrectionRepository()

        container = ReviewRepositories(
            jobs=jobs,  # type: ignore[arg-type]
            tracks=tracks,  # type: ignore[arg-type]
            decisions=decisions,  # type: ignore[arg-type]
            corrections=corrections,  # type: ignore[arg-type]
        )

        assert container.jobs is jobs
        assert container.tracks is tracks
        assert container.decisions is decisions
        assert container.corrections is corrections

    def test_initialization_raises_value_error_for_none_corrections(self) -> None:
        """Test that ValueError is raised when corrections is None."""
        from playlist_bridge.ports import ReviewRepositories

        with pytest.raises(ValueError, match="corrections repository cannot be None"):
            ReviewRepositories(
                jobs=None,  # type: ignore[arg-type]
                tracks=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
            )


class TestMatcherDependencies:
    """Test MatcherDependencies dependency container."""

    def test_initialization_with_valid_dependencies(self) -> None:
        """Test successful initialization with valid dependencies."""
        from playlist_bridge.ports import (
            MatchDecisionRepository,
            MatchCacheRepository,
            ManualCorrectionRepository,
            MatchingConfig,
            Clock,
            MatcherDependencies,
        )

        class FakeSpotify:
            pass

        class FakeDecisionRepository:
            pass

        class FakeCacheRepository:
            pass

        class FakeCorrectionRepository:
            pass

        spotify = FakeSpotify()
        decisions = FakeDecisionRepository()
        match_cache = FakeCacheRepository()
        corrections = FakeCorrectionRepository()
        config = MatchingConfig(
            schema_version=1,
            title_weight=0.3,
            artist_weight=0.3,
            duration_weight=0.2,
            version_weight=0.1,
            explicit_weight=0.1,
            unwanted_version_penalty=0.5,
            version_contradiction_penalty=0.5,
            explicit_mismatch_penalty=0.5,
            duration_full_credit_floor_ms=3000,
            duration_full_credit_ratio=0.05,
            duration_zero_credit_floor_ms=30000,
            duration_zero_credit_ratio=0.5,
            max_queries_per_track=5,
            results_per_query=10,
            max_unique_candidates=20,
            cache_freshness_days=30,
            policy_thresholds={
                MatchPolicy.STRICT: {
                    "min_score": 0.8,
                    "title_threshold": 0.7,
                    "artist_threshold": 0.7,
                    "duration_threshold": 0.7,
                },
                MatchPolicy.BALANCED: {
                    "min_score": 0.5,
                    "title_threshold": 0.5,
                    "artist_threshold": 0.5,
                    "duration_threshold": 0.5,
                },
                MatchPolicy.LOOSE: {
                    "min_score": 0.3,
                    "title_threshold": 0.3,
                    "artist_threshold": 0.3,
                    "duration_threshold": 0.3,
                },
            },
        )

        def clock():
            from datetime import datetime
            return datetime.now()

        container = MatcherDependencies(
            spotify=spotify,  # type: ignore[arg-type]
            decisions=decisions,  # type: ignore[arg-type]
            match_cache=match_cache,  # type: ignore[arg-type]
            corrections=corrections,  # type: ignore[arg-type]
            matching_config=config,
            clock=clock,
        )

        assert container.spotify is spotify
        assert container.decisions is decisions
        assert container.match_cache is match_cache
        assert container.corrections is corrections
        assert container.matching_config is config
        assert container.clock is clock

    def test_initialization_raises_value_error_for_none_spotify(self) -> None:
        """Test that ValueError is raised when spotify is None."""
        from playlist_bridge.ports import MatcherDependencies

        with pytest.raises(ValueError, match="spotify adapter cannot be None"):
            MatcherDependencies(
                spotify=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                match_cache=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
                matching_config=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_decisions(self) -> None:
        """Test that ValueError is raised when decisions is None."""
        from playlist_bridge.ports import MatcherDependencies

        with pytest.raises(ValueError, match="decisions repository cannot be None"):
            MatcherDependencies(
                spotify=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                match_cache=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
                matching_config=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_match_cache(self) -> None:
        """Test that ValueError is raised when match_cache is None."""
        from playlist_bridge.ports import MatcherDependencies

        with pytest.raises(ValueError, match="match_cache repository cannot be None"):
            MatcherDependencies(
                spotify=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                match_cache=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
                matching_config=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_corrections(self) -> None:
        """Test that ValueError is raised when corrections is None."""
        from playlist_bridge.ports import MatcherDependencies

        with pytest.raises(ValueError, match="corrections repository cannot be None"):
            MatcherDependencies(
                spotify=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                match_cache=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
                matching_config=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_matching_config(self) -> None:
        """Test that ValueError is raised when matching_config is None."""
        from playlist_bridge.ports import MatcherDependencies

        with pytest.raises(ValueError, match="matching_config cannot be None"):
            MatcherDependencies(
                spotify=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                match_cache=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
                matching_config=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
            )

    def test_initialization_raises_value_error_for_none_clock(self) -> None:
        """Test that ValueError is raised when clock is None."""
        from playlist_bridge.ports import MatcherDependencies

        with pytest.raises(ValueError, match="clock cannot be None"):
            MatcherDependencies(
                spotify=None,  # type: ignore[arg-type]
                decisions=None,  # type: ignore[arg-type]
                match_cache=None,  # type: ignore[arg-type]
                corrections=None,  # type: ignore[arg-type]
                matching_config=None,  # type: ignore[arg-type]
                clock=None,  # type: ignore[arg-type]
            )


# ============================================================================
# Tests for error types
# ============================================================================


class TestRepositoryErrorTypes:
    """Test repository error types."""

    def test_job_not_found_error(self) -> None:
        """Test JobNotFoundError initialization."""
        from playlist_bridge.ports import JobNotFoundError
        err = JobNotFoundError("job-123")
        assert err.job_id == "job-123"
        assert "Job not found: job-123" in str(err)

    def test_job_lease_busy_error(self) -> None:
        """Test JobLeaseBusyError initialization."""
        from playlist_bridge.ports import JobLeaseBusyError
        err = JobLeaseBusyError("job-123", "worker-456")
        assert err.job_id == "job-123"
        assert err.owner_id == "worker-456"
        assert "job-123" in str(err)
        assert "worker-456" in str(err)

    def test_lease_lost_error(self) -> None:
        """Test LeaseLostError initialization."""
        from playlist_bridge.ports import LeaseLostError
        err = LeaseLostError("job-123")
        assert err.job_id == "job-123"
        assert "Lease lost for job: job-123" in str(err)
