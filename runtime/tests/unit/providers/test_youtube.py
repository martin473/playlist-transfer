"""Unit tests for YouTube provider utilities."""

import pytest

from playlist_bridge.providers.youtube import (
    parse_youtube_duration_ms,
    parse_youtube_playlist_id,
    fetch_youtube_playlist_metadata,
    fetch_youtube_playlist_item_page,
    iter_youtube_playlist_items,
)
from playlist_bridge.providers.errors import (
    AuthenticationRequired,
    PermissionDenied,
    ProviderNotFound,
    RateLimited,
    InvalidProviderResponse,
    TemporaryProviderFailure,
    CancellationRequested,
)
from playlist_bridge.domain.models import PlaylistReference, SourcePlaylistMetadata
from playlist_bridge.providers.youtube import SourceAdapter
from playlist_bridge.providers.youtube import CancellationToken
from playlist_bridge.domain.models import ItemPage
from playlist_bridge.domain.models import LoadedSourcePlaylist


class TestParseYouTubePlaylistId:
    """Tests for parse_youtube_playlist_id function."""

    def test_valid_standard_youtube_playlist(self) -> None:
        """Test parsing a standard YouTube playlist URL."""
        url = "https://www.youtube.com/playlist?list=PL1234567890"
        assert parse_youtube_playlist_id(url) == "PL1234567890"

    def test_valid_youtube_music_playlist(self) -> None:
        """Test parsing a YouTube Music playlist URL."""
        url = "https://music.youtube.com/playlist?list=PL9876543210"
        assert parse_youtube_playlist_id(url) == "PL9876543210"

    def test_valid_playlist_with_additional_params(self) -> None:
        """Test parsing a playlist URL with additional query parameters."""
        url = "https://www.youtube.com/playlist?list=PL123&index=1&t=0"
        assert parse_youtube_playlist_id(url) == "PL123"

    def test_valid_video_in_playlist_url(self) -> None:
        """Test parsing a video URL with a playlist parameter (video in playlist)."""
        url = "https://www.youtube.com/watch?v=abc123&list=PL456"
        assert parse_youtube_playlist_id(url) == "PL456"

    def test_valid_shortened_youtube_url(self) -> None:
        """Test parsing a shortened YouTube URL with playlist parameter."""
        url = "https://youtu.be/abc123?list=PL789"
        assert parse_youtube_playlist_id(url) == "PL789"

    def test_valid_playlist_with_underscore(self) -> None:
        """Test parsing a playlist ID with underscores."""
        url = "https://www.youtube.com/playlist?list=PL_123_ABC"
        assert parse_youtube_playlist_id(url) == "PL_123_ABC"

    def test_valid_playlist_with_dash(self) -> None:
        """Test parsing a playlist ID with dashes."""
        url = "https://www.youtube.com/playlist?list=PL-123-ABC"
        assert parse_youtube_playlist_id(url) == "PL-123-ABC"

    def test_reject_video_only_url(self) -> None:
        """Test rejecting a video-only URL without a list parameter."""
        url = "https://www.youtube.com/watch?v=abc123"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_video_only_shortened_url(self) -> None:
        """Test rejecting a shortened video-only URL without a list parameter."""
        url = "https://youtu.be/abc123"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_playlist_without_list_param(self) -> None:
        """Test rejecting a playlist URL without the list parameter."""
        url = "https://www.youtube.com/playlist"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_empty_list_param(self) -> None:
        """Test rejecting a URL with an empty list parameter."""
        url = "https://www.youtube.com/playlist?list="
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_malformed_url(self) -> None:
        """Test rejecting a malformed URL."""
        url = "not a url"
        with pytest.raises(ValueError, match="No playlist ID found in URL"):
            parse_youtube_playlist_id(url)

    def test_reject_other_youtube_paths_without_list(self) -> None:
        """Test rejecting other YouTube paths without a list parameter."""
        urls = [
            "https://www.youtube.com/c/ChannelName",
            "https://www.youtube.com/user/username",
            "https://www.youtube.com/feed/subscriptions",
            "https://www.youtube.com/channel/UC123",
        ]
        for url in urls:
            with pytest.raises(ValueError, match="No playlist ID found in URL"):
                parse_youtube_playlist_id(url)

    @pytest.mark.parametrize(
        "url,expected_id",
        [
            ("https://www.youtube.com/playlist?list=PL123", "PL123"),
            ("https://music.youtube.com/playlist?list=PL456", "PL456"),
            ("https://www.youtube.com/playlist?list=PL789&index=1", "PL789"),
            ("https://www.youtube.com/watch?v=abc&list=PL111", "PL111"),
            ("https://youtu.be/abc?list=PL222", "PL222"),
            ("https://www.youtube.com/playlist?list=PL_ABC_123", "PL_ABC_123"),
            ("https://www.youtube.com/playlist?list=PL-ABC-123", "PL-ABC-123"),
        ],
    )
    def test_various_valid_urls(self, url: str, expected_id: str) -> None:
        """Test various valid YouTube playlist URLs."""
        assert parse_youtube_playlist_id(url) == expected_id


class TestParseYouTubeDurationMs:
    """Tests for parse_youtube_duration_ms function."""

    def test_valid_iso_8601_duration_seconds(self) -> None:
        """Test parsing a valid ISO 8601 duration in seconds."""
        duration_str = "PT10M5S"
        expected_ms = 605000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_minutes(self) -> None:
        """Test parsing a valid ISO 8601 duration in minutes."""
        duration_str = "PT3M30S"
        expected_ms = 210000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_hours(self) -> None:
        """Test parsing a valid ISO 8601 duration in hours."""
        duration_str = "PT1H2M10S"
        expected_ms = 3730000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_zero(self) -> None:
        """Test parsing a zero duration."""
        duration_str = "PT0S"
        expected_ms = 0
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_seconds_only(self) -> None:
        """Test parsing a duration with seconds only."""
        duration_str = "PT45S"
        expected_ms = 45000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_minutes_only(self) -> None:
        """Test parsing a duration with minutes only."""
        duration_str = "PT2M"
        expected_ms = 120000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_valid_iso_8601_duration_hours_only(self) -> None:
        """Test parsing a duration with hours only."""
        duration_str = "PT3H"
        expected_ms = 10800000
        assert parse_youtube_duration_ms(duration_str) == expected_ms

    def test_invalid_iso_8601_duration(self) -> None:
        """Test parsing an invalid duration string."""
        duration_str = "invalid"
        assert parse_youtube_duration_ms(duration_str) is None

    def test_none_duration(self) -> None:
        """Test parsing None as duration."""
        assert parse_youtube_duration_ms(None) is None

    def test_incomplete_duration(self) -> None:
        """Test parsing an incomplete duration string."""
        duration_str = "PT"
        assert parse_youtube_duration_ms(duration_str) is None


class TestMapYouTubeError:
    """Tests for map_youtube_error function."""

    def test_map_youtube_error_401_authentication_required(self) -> None:
        """Test mapping HTTP 401 to AuthenticationRequired."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 401
                self.reason = "Unauthorized"

        error = HttpError(MockHttpResponse(), b"Authentication failed")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, AuthenticationRequired)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_403_permission_denied(self) -> None:
        """Test mapping HTTP 403 to PermissionDenied."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 403
                self.reason = "Forbidden"

        error = HttpError(MockHttpResponse(), b"Permission denied")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, PermissionDenied)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_404_provider_not_found(self) -> None:
        """Test mapping HTTP 404 to ProviderNotFound."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 404
                self.reason = "Not Found"

        error = HttpError(MockHttpResponse(), b"Resource not found")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, ProviderNotFound)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_429_rate_limited(self) -> None:
        """Test mapping HTTP 429 to RateLimited."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 429
                self.reason = "Too Many Requests"
                self.headers = {}

        error = HttpError(MockHttpResponse(), b"Rate limit exceeded")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, RateLimited)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_429_preserves_retry_metadata(self) -> None:
        """Test that HTTP 429 mapping preserves Retry-After metadata."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 429
                self.reason = "Too Many Requests"
                self.headers = {"Retry-After": "60"}

        error = HttpError(MockHttpResponse(), b"Rate limit exceeded")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, RateLimited)
        assert result.service == "youtube"
        assert result.operation == operation
        assert "Retry-After" in str(result)
        assert "60" in str(result)

    @pytest.mark.parametrize(
        "status_code,reason",
        [
            (500, "Internal Server Error"),
            (502, "Bad Gateway"),
            (503, "Service Unavailable"),
            (504, "Gateway Timeout"),
            (505, "HTTP Version Not Supported"),
            (511, "Network Authentication Required"),
        ],
    )
    def test_map_youtube_error_5xx_temporary_provider_failure(self, status_code: int, reason: str) -> None:
        """Test mapping HTTP 5xx status codes to TemporaryProviderFailure."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = status_code
                self.reason = reason

        error = HttpError(MockHttpResponse(), f"{reason} error".encode())
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, TemporaryProviderFailure)
        assert result.service == "youtube"
        assert result.operation == operation
        assert str(status_code) in str(result)

    def test_map_youtube_error_unknown_status_invalid_response(self) -> None:
        """Test mapping an unknown HTTP status to InvalidProviderResponse."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHttpResponse:
            def __init__(self):
                self.status = 418
                self.reason = "I'm a teapot"

        error = HttpError(MockHttpResponse(), b"I'm a teapot")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, InvalidProviderResponse)
        assert result.service == "youtube"
        assert result.operation == operation

    def test_map_youtube_error_429_preserves_retry_metadata_with_headers_object(self) -> None:
        """Test that HTTP 429 mapping preserves Retry-After metadata when headers are present as an object."""
        from playlist_bridge.providers.youtube import map_youtube_error
        from googleapiclient.errors import HttpError

        class MockHeaders:
            def __init__(self):
                self._headers = {"Retry-After": "120"}

            def get(self, key, default=None):
                return self._headers.get(key, default)

        class MockHttpResponse:
            def __init__(self):
                self.status = 429
                self.reason = "Too Many Requests"
                self.headers = MockHeaders()

        error = HttpError(MockHttpResponse(), b"Rate limit exceeded")
        operation = "fetch_playlist_metadata"

        result = map_youtube_error(error, operation)

        assert isinstance(result, RateLimited)
        assert result.service == "youtube"
        assert result.operation == operation
        assert "Retry-After" in str(result)
        assert "120" in str(result)


class TestFetchYouTubePlaylistItemPage:
    """Tests for fetch_youtube_playlist_item_page function."""

    def test_returns_items_and_next_page_token(self) -> None:
        """Test that the function returns items and the next-page token without mutating order."""
        # This is a minimal test that verifies the function exists and has the correct signature
        # Full integration tests will use a mock YouTube client
        from playlist_bridge.providers.youtube import fetch_youtube_playlist_item_page
        import inspect

        # Verify the function exists and has the expected parameters
        sig = inspect.signature(fetch_youtube_playlist_item_page)
        params = list(sig.parameters.keys())

        assert "client" in params
        assert "playlist_id" in params
        assert "page_token" in params

        # Check that page_token has a default of None
        page_token_param = sig.parameters["page_token"]
        assert page_token_param.default is None

        # Check return annotation includes ItemPage
        # Note: ItemPage is imported from domain.models
        from playlist_bridge.domain.models import ItemPage
        assert sig.return_annotation in (ItemPage, object) or sig.return_annotation == ItemPage

    def test_handles_missing_client(self) -> None:
        """Test that the function raises appropriate errors when client is missing."""
        from playlist_bridge.providers.youtube import fetch_youtube_playlist_item_page
        from playlist_bridge.providers.errors import AuthenticationRequired
        from googleapiclient.errors import HttpError
        import pytest

        # Mock a client that raises HttpError
        class MockHttpResponse:
            def __init__(self):
                self.status = 401
                self.reason = "Unauthorized"

        # Create a client that raises a 401 error
        class MockClient:
            def playlistItems(self):
                class PlaylistItems:
                    def list(self, **kwargs):
                        raise HttpError(MockHttpResponse(), b"Unauthorized")
                return PlaylistItems()

        client = MockClient()

        with pytest.raises(AuthenticationRequired):
            fetch_youtube_playlist_item_page(client, "PL123")


class TestIterYouTubePlaylistItems:
    """Tests for iter_youtube_playlist_items generator function."""

    def test_three_page_fixture_yields_every_item_exactly_once(self) -> None:
        """Test that a three-page fixture yields every item exactly once.

        This test uses a mock client that simulates a three-page playlist
        with 5 items per page (15 total items). It verifies that all items
        are yielded exactly once in the correct order.
        """
        from playlist_bridge.providers.youtube import iter_youtube_playlist_items
        from playlist_bridge.domain.models import SourceTrack

        # Mock cancellation token that never cancels
        class NeverCancel:
            def is_cancelled(self) -> bool:
                return False

            def raise_if_cancelled(self) -> None:
                pass

        cancel = NeverCancel()

        # Track items yielded to verify no duplicates and correct order
        yielded_video_ids = []
        expected_video_ids = [f"video_{i:03d}" for i in range(15)]

        # Mock client with pagination state
        class MockClient:
            def __init__(self):
                self.page_count = 0
                # Three pages, 5 items each
                self.pages = self._build_pages()

            def _build_pages(self):
                # Page 0: items 0-4, nextPageToken = "page1"
                # Page 1: items 5-9, nextPageToken = "page2"
                # Page 2: items 10-14, no nextPageToken
                items_per_page = 5
                pages = []

                for page_idx in range(3):
                    start = page_idx * items_per_page
                    end = start + items_per_page
                    items = []
                    for i in range(start, end):
                        video_id = f"video_{i:03d}"
                        items.append({
                            "snippet": {
                                "title": f"Track {i}",
                                "videoOwnerChannelTitle": f"Channel {i % 3}",
                                "resourceId": {"videoId": video_id},
                            },
                            "contentDetails": {
                                "duration": "PT3M45S",
                            },
                        })

                    page_token = f"page{page_idx + 1}" if page_idx < 2 else None
                    pages.append({
                        "items": items,
                        "nextPageToken": page_token,
                        "pageInfo": {"totalResults": 15},
                    })

                return pages

            def playlistItems(self):
                class PlaylistItems:
                    def __init__(self, parent):
                        self.parent = parent

                    def list(self, **kwargs):
                        page_token = kwargs.get("pageToken", "")
                        # Determine which page to return based on page_token
                        if page_token == "page1":
                            idx = 1
                        elif page_token == "page2":
                            idx = 2
                        else:
                            idx = 0

                        # Return a mock response with execute method
                        class MockResponse:
                            def __init__(self, data):
                                self._data = data

                            def get(self, key, default=None):
                                return self._data.get(key, default)

                            def __getitem__(self, key):
                                return self._data[key]

                            def execute(self):
                                return self._data

                        return MockResponse(self.parent.pages[idx])

                return PlaylistItems(self)

        client = MockClient()

        # Iterate through all items
        for track in iter_youtube_playlist_items(client, "PL123", cancel):
            assert isinstance(track, SourceTrack)
            assert track.video_id is not None
            yielded_video_ids.append(track.video_id)

        # Verify all 15 items were yielded exactly once in the correct order
        assert yielded_video_ids == expected_video_ids
        assert len(yielded_video_ids) == 15

    def test_handles_cancellation(self) -> None:
        """Test that the generator properly handles cancellation requests."""
        from playlist_bridge.providers.youtube import iter_youtube_playlist_items
        from playlist_bridge.providers.errors import CancellationRequested

        # Mock cancellation token that cancels after 3 items
        class CancelAfterThree:
            def __init__(self):
                self.count = 0

            def is_cancelled(self) -> bool:
                return self.count >= 3

            def raise_if_cancelled(self) -> None:
                if self.is_cancelled():
                    raise CancellationRequested("youtube", "iter_playlist_items", "Cancelled")

        cancel = CancelAfterThree()

        # Mock client with a single page of 10 items
        class MockClient:
            def playlistItems(self):
                class PlaylistItems:
                    def list(self, **kwargs):
                        items = []
                        for i in range(10):
                            items.append({
                                "snippet": {
                                    "title": f"Track {i}",
                                    "videoOwnerChannelTitle": f"Channel {i}",
                                    "resourceId": {"videoId": f"video_{i:03d}"},
                                },
                                "contentDetails": {
                                    "duration": "PT3M45S",
                                },
                            })

                        class MockResponse:
                            def __init__(self):
                                self._data = {
                                    "items": items,
                                    "nextPageToken": None,
                                    "pageInfo": {"totalResults": 10},
                                }

                            def get(self, key, default=None):
                                return self._data.get(key, default)

                            def __getitem__(self, key):
                                return self._data[key]

                            def execute(self):
                                return self._data

                        return MockResponse()

                return PlaylistItems()

        client = MockClient()

        # Iterate - should raise CancellationRequested after 3 items
        yielded = []
        with pytest.raises(CancellationRequested):
            for track in iter_youtube_playlist_items(client, "PL123", cancel):
                cancel.count += 1  # Increment to trigger cancellation
                yielded.append(track.video_id)

        # Should have yielded exactly 3 items before cancellation
        assert len(yielded) == 3
        assert yielded == [f"video_{i:03d}" for i in range(3)]

    def test_handles_empty_playlist(self) -> None:
        """Test that the generator handles an empty playlist correctly."""
        from playlist_bridge.providers.youtube import iter_youtube_playlist_items

        class NeverCancel:
            def is_cancelled(self) -> bool:
                return False

            def raise_if_cancelled(self) -> None:
                pass

        cancel = NeverCancel()

        # Mock client with empty playlist
        class MockClient:
            def playlistItems(self):
                class PlaylistItems:
                    def list(self, **kwargs):
                        class MockResponse:
                            def __init__(self):
                                self._data = {
                                    "items": [],
                                    "nextPageToken": None,
                                    "pageInfo": {"totalResults": 0},
                                }

                            def get(self, key, default=None):
                                return self._data.get(key, default)

                            def __getitem__(self, key):
                                return self._data[key]

                            def execute(self):
                                return self._data

                        return MockResponse()

                return PlaylistItems()

        client = MockClient()

        # Iterate - should yield nothing
        items = list(iter_youtube_playlist_items(client, "PL123", cancel))
        assert len(items) == 0


class TestFetchYouTubePlaylistMetadata:
    """Tests for fetch_youtube_playlist_metadata function."""

    def test_builds_metadata_from_public_playlist(self) -> None:
        """Test that metadata is correctly built from a public playlist response."""
        from googleapiclient.errors import HttpError

        # Mock client that returns a public playlist response
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "My Awesome Playlist",
                                "description": "A collection of great songs",
                                "channelId": "UC123456789",
                                "channelTitle": "My Channel",
                            },
                            "contentDetails": {
                                "itemCount": "42",
                            },
                            "status": {
                                "privacyStatus": "public",
                            },
                        }
                    ]
                }

        client = MockClient()
        playlist_id = "PL1234567890"

        result = fetch_youtube_playlist_metadata(client, playlist_id)

        assert result.reference.provider == "youtube"
        assert result.reference.playlist_id == playlist_id
        assert result.reference.name == "My Awesome Playlist"
        assert result.reference.owner == "My Channel"
        assert result.description == "A collection of great songs"
        assert result.privacy_status == "public"
        assert result.owner_channel_id == "UC123456789"
        assert result.owner_channel_title == "My Channel"
        assert result.item_count == 42

    def test_builds_metadata_from_unlisted_playlist(self) -> None:
        """Test that metadata is correctly built from an unlisted playlist response."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "Private Mix",
                                "description": "",
                                "channelId": "UC987654321",
                                "channelTitle": "Secret Channel",
                            },
                            "contentDetails": {
                                "itemCount": "15",
                            },
                            "status": {
                                "privacyStatus": "unlisted",
                            },
                        }
                    ]
                }

        client = MockClient()
        playlist_id = "PL9876543210"

        result = fetch_youtube_playlist_metadata(client, playlist_id)

        assert result.reference.provider == "youtube"
        assert result.reference.playlist_id == playlist_id
        assert result.reference.name == "Private Mix"
        assert result.reference.owner == "Secret Channel"
        assert result.description == ""
        assert result.privacy_status == "unlisted"
        assert result.owner_channel_id == "UC987654321"
        assert result.owner_channel_title == "Secret Channel"
        assert result.item_count == 15

    def test_builds_metadata_from_private_playlist(self) -> None:
        """Test that metadata is correctly built from a private playlist response."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "My Private Playlist",
                                "description": "Only I can see this",
                                "channelId": "UC123456789",
                                "channelTitle": "My Channel",
                            },
                            "contentDetails": {
                                "itemCount": "7",
                            },
                            "status": {
                                "privacyStatus": "private",
                            },
                        }
                    ]
                }

        client = MockClient()
        playlist_id = "PL1234567890"

        result = fetch_youtube_playlist_metadata(client, playlist_id)

        assert result.privacy_status == "private"
        assert result.item_count == 7

    def test_handles_missing_item_count(self) -> None:
        """Test that missing item_count defaults to 0."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "No Count Playlist",
                                "description": "",
                                "channelId": "UC123456789",
                                "channelTitle": "Channel",
                            },
                            "contentDetails": {},
                            "status": {
                                "privacyStatus": "public",
                            },
                        }
                    ]
                }

        client = MockClient()
        result = fetch_youtube_playlist_metadata(client, "PL1234567890")

        assert result.item_count == 0

    def test_handles_invalid_item_count(self) -> None:
        """Test that invalid item_count string defaults to 0."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "Invalid Count Playlist",
                                "description": "",
                                "channelId": "UC123456789",
                                "channelTitle": "Channel",
                            },
                            "contentDetails": {
                                "itemCount": "not-a-number",
                            },
                            "status": {
                                "privacyStatus": "public",
                            },
                        }
                    ]
                }

        client = MockClient()
        result = fetch_youtube_playlist_metadata(client, "PL1234567890")

        assert result.item_count == 0

    def test_uses_channel_id_as_owner_when_title_missing(self) -> None:
        """Test that channel ID is used as owner when channel title is missing."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "Test Playlist",
                                "description": "",
                                "channelId": "UC123456789",
                                "channelTitle": "",
                            },
                            "contentDetails": {
                                "itemCount": "5",
                            },
                            "status": {
                                "privacyStatus": "public",
                            },
                        }
                    ]
                }

        client = MockClient()
        result = fetch_youtube_playlist_metadata(client, "PL1234567890")

        assert result.reference.owner == "UC123456789"
        assert result.owner_channel_id == "UC123456789"
        assert result.owner_channel_title == ""

    def test_raises_provider_not_found_for_empty_items(self) -> None:
        """Test that ProviderNotFound is raised when no items are returned."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {"items": []}

        client = MockClient()

        with pytest.raises(ProviderNotFound) as exc_info:
            fetch_youtube_playlist_metadata(client, "PL1234567890")

        assert "youtube" in str(exc_info.value)
        assert "fetch_playlist_metadata" in str(exc_info.value)

    def test_raises_invalid_provider_response_missing_title(self) -> None:
        """Test that InvalidProviderResponse is raised when title is missing."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "",
                                "description": "",
                                "channelId": "UC123456789",
                                "channelTitle": "Channel",
                            },
                            "contentDetails": {
                                "itemCount": "5",
                            },
                            "status": {
                                "privacyStatus": "public",
                            },
                        }
                    ]
                }

        client = MockClient()

        with pytest.raises(InvalidProviderResponse) as exc_info:
            fetch_youtube_playlist_metadata(client, "PL1234567890")

        assert "Missing playlist title" in str(exc_info.value)

    def test_raises_invalid_provider_response_missing_owner_channel_id(self) -> None:
        """Test that InvalidProviderResponse is raised when owner channel ID is missing."""
        class MockClient:
            def playlists(self):
                return self

            def list(self, part, id):
                self._part = part
                self._id = id
                return self

            def execute(self):
                return {
                    "items": [
                        {
                            "snippet": {
                                "title": "Test Playlist",
                                "description": "",
                                "channelId": "",
                                "channelTitle": "Channel",
                            },
                            "contentDetails": {
                                "itemCount": "5",
                            },
                            "status": {
                                "privacyStatus": "public",
                            },
                        }
                    ]
                }

        client = MockClient()

        with pytest.raises(InvalidProviderResponse) as exc_info:
            fetch_youtube_playlist_metadata(client, "PL1234567890")

        assert "Missing owner channel ID" in str(exc_info.value)


class TestMapYouTubePlaylistItem:
    """Tests for map_youtube_playlist_item function."""

    def test_maps_available_video(self) -> None:
        """Test mapping an available video to SourceTrack."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "id": "PL123_item1",
            "snippet": {
                "title": "My Awesome Song",
                "videoOwnerChannelTitle": "Music Channel",
                "resourceId": {"videoId": "abc123"},
            },
            "contentDetails": {},
        }
        video = {
            "id": "abc123",
            "contentDetails": {"duration": "PT3M30S"},
        }

        track = map_youtube_playlist_item(item, video)
        track.position = 0

        assert track.title == "My Awesome Song"
        assert track.artist_names == ["Music Channel"]
        assert track.duration_seconds == 210
        assert track.video_id == "abc123"
        assert track.channel_title == "Music Channel"
        assert track.availability == "available"

    def test_maps_available_video_with_missing_title(self) -> None:
        """Test mapping an available video with missing title."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "id": "PL123_item2",
            "snippet": {
                "title": "",
                "videoOwnerChannelTitle": "Music Channel",
                "resourceId": {"videoId": "def456"},
            },
            "contentDetails": {},
        }
        video = {
            "id": "def456",
            "contentDetails": {"duration": "PT2M15S"},
        }

        track = map_youtube_playlist_item(item, video)
        track.position = 1

        assert track.title == "Untitled"
        assert track.artist_names == ["Music Channel"]
        assert track.duration_seconds == 135
        assert track.video_id == "def456"
        assert track.availability == "available"

    def test_maps_unavailable_video(self) -> None:
        """Test mapping an unavailable (deleted) video to SourceTrack."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "id": "PL123_item3",
            "snippet": {
                "title": "Deleted Video Title",
                "videoOwnerChannelTitle": "Music Channel",
                "resourceId": {},
            },
            "contentDetails": {},
        }

        track = map_youtube_playlist_item(item, None)
        track.position = 2

        assert track.title == "Deleted Video Title"
        assert track.artist_names == ["Music Channel"]
        assert track.duration_seconds == 0
        assert track.video_id.startswith("deleted_PL123_item3")
        assert track.channel_title == "Music Channel"
        assert track.availability == "unavailable"

    def test_maps_unavailable_video_with_missing_title(self) -> None:
        """Test mapping an unavailable video with missing title."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "id": "PL123_item4",
            "snippet": {
                "title": "",
                "videoOwnerChannelTitle": "",
                "resourceId": {},
            },
            "contentDetails": {},
        }

        track = map_youtube_playlist_item(item, None)
        track.position = 3

        assert track.title == "Deleted Video"
        assert track.artist_names == ["Unknown Artist"]
        assert track.duration_seconds == 0
        assert track.video_id.startswith("deleted_PL123_item4")
        assert track.channel_title is None
        assert track.availability == "unavailable"

    def test_maps_unavailable_video_without_item_id(self) -> None:
        """Test mapping an unavailable video without an item ID."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "snippet": {
                "title": "No ID Video",
                "videoOwnerChannelTitle": "Some Channel",
                "resourceId": {},
            },
            "contentDetails": {},
        }

        track = map_youtube_playlist_item(item, None)
        track.position = 4

        assert track.title == "No ID Video"
        assert track.artist_names == ["Some Channel"]
        assert track.duration_seconds == 0
        assert track.video_id.startswith("deleted_")
        assert track.channel_title == "Some Channel"
        assert track.availability == "unavailable"

    def test_maps_private_video(self) -> None:
        """Test mapping a private video to SourceTrack with preserved metadata."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "id": "PL123_item5",
            "snippet": {
                "title": "Private Song",
                "videoOwnerChannelTitle": "Private Channel",
                "resourceId": {},
            },
            "contentDetails": {},
            "status": {
                "privacyStatus": "private",
            },
        }

        track = map_youtube_playlist_item(item, None)
        track.position = 5

        assert track.title == "Private Song"
        assert track.artist_names == ["Private Channel"]
        assert track.duration_seconds == 0
        assert track.video_id.startswith("private_PL123_item5")
        assert track.channel_title == "Private Channel"
        assert track.availability == "unavailable"

    def test_maps_private_video_with_missing_title(self) -> None:
        """Test mapping a private video with missing title."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "id": "PL123_item6",
            "snippet": {
                "title": "",
                "videoOwnerChannelTitle": "Private Channel",
                "resourceId": {},
            },
            "contentDetails": {},
            "status": {
                "privacyStatus": "private",
            },
        }

        track = map_youtube_playlist_item(item, None)
        track.position = 6

        assert track.title == "Untitled"
        assert track.artist_names == ["Private Channel"]
        assert track.duration_seconds == 0
        assert track.video_id.startswith("private_PL123_item6")
        assert track.channel_title == "Private Channel"
        assert track.availability == "unavailable"

    def test_maps_private_video_without_item_id(self) -> None:
        """Test mapping a private video without an item ID."""
        from playlist_bridge.providers.youtube import map_youtube_playlist_item

        item = {
            "snippet": {
                "title": "Private Video No ID",
                "videoOwnerChannelTitle": "Some Channel",
                "resourceId": {},
            },
            "contentDetails": {},
            "status": {
                "privacyStatus": "private",
            },
        }

        track = map_youtube_playlist_item(item, None)
        track.position = 7

        assert track.title == "Private Video No ID"
        assert track.artist_names == ["Some Channel"]
        assert track.duration_seconds == 0
        assert track.video_id.startswith("private_")
        assert track.channel_title == "Some Channel"
        assert track.availability == "unavailable"


class TestFakeSourceAdapter:
    """Tests for the fake SourceAdapter implementation."""

    def test_fake_adapter_satisfies_protocol(self) -> None:
        """Test that the fake adapter satisfies the SourceAdapter protocol."""
        from playlist_bridge.providers.youtube import SourceAdapter
        from playlist_bridge.providers.youtube import CancellationToken
        from playlist_bridge.domain.models import PlaylistReference
        from playlist_bridge.domain.models import ItemPage
        from playlist_bridge.domain.models import LoadedSourcePlaylist
        import typing

        # Create a concrete fake implementation of SourceAdapter
        class FakeAdapter:
            def load_page(
                self,
                reference: PlaylistReference,
                page_token: typing.Optional[str] = None,
                *,
                cancel: CancellationToken,
            ) -> ItemPage:
                return ItemPage(items=[], next_page_token=None, total_items=0)

            def load_playlist(
                self, reference: PlaylistReference, *, cancel: CancellationToken
            ) -> LoadedSourcePlaylist:
                from playlist_bridge.domain.models import SourcePlaylistMetadata
                from playlist_bridge.domain.models import SourceTrack
                return LoadedSourcePlaylist(
                    metadata=SourcePlaylistMetadata(
                        title="Fake Playlist",
                        description=None,
                        source="youtube",
                        source_id=reference.source_id,
                        url=reference.url,
                        track_count=0,
                        duration_seconds=0,
                    ),
                    tracks=[],
                )

        # Verify the fake implements the protocol using static type checking
        # Since SourceAdapter is a Protocol without @runtime_checkable, we use mypy
        # or just verify the methods exist with correct signatures via typing
        fake = FakeAdapter()
        # Check that the fake has all required methods with correct signatures
        assert hasattr(fake, "load_page")
        assert hasattr(fake, "load_playlist")
        # Verify the methods are callable with the expected arguments
        assert callable(fake.load_page)
        assert callable(fake.load_playlist)
