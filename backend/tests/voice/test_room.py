"""
Unit tests for voice.room module.

Tests Daily.co room creation factory.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import json

from backend.app.voice.room import create_daily_room


class TestCreateDailyRoom:
    """Test create_daily_room factory function."""

    @pytest.mark.asyncio
    async def test_returns_room_url_string(self, mock_settings):
        """Test that function returns a room URL string."""
        room_url = "https://example.daily.co/test-room"

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": room_url}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock(
                return_value=mock_response.__aenter__.return_value
            )
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            result = await create_daily_room()

            assert isinstance(result, str)
            assert "daily.co" in result or result == room_url

    @pytest.mark.asyncio
    async def test_default_expiry_seconds(self, mock_settings):
        """Test default expiry time is 3600 seconds."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://example.daily.co/test"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with patch("time.time", return_value=1000):
                await create_daily_room()

                # Check that expiry calculation includes default 3600
                call_args = mock_session.post.call_args
                json_data = call_args.kwargs.get("json", {})
                exp_value = json_data.get("properties", {}).get("exp")

                # exp should be approximately current_time + 3600
                assert exp_value == int(1000 + 3600)

    @pytest.mark.asyncio
    async def test_custom_expiry_seconds(self, mock_settings):
        """Test with custom expiry time."""
        custom_expiry = 7200

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://example.daily.co/test"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with patch("time.time", return_value=1000):
                await create_daily_room(expiry_seconds=custom_expiry)

                call_args = mock_session.post.call_args
                json_data = call_args.kwargs.get("json", {})
                exp_value = json_data.get("properties", {}).get("exp")

                assert exp_value == int(1000 + custom_expiry)

    @pytest.mark.asyncio
    async def test_posts_to_daily_api(self, mock_settings):
        """Test that request is posted to Daily API."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://example.daily.co/test"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            await create_daily_room()

            call_args = mock_session.post.call_args
            assert call_args[0][0] == "https://api.daily.co/v1/rooms"

    @pytest.mark.asyncio
    async def test_includes_authorization_header(self, mock_settings):
        """Test that authorization header is included."""
        mock_settings.daily_api_key = "test-daily-key-123"

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://example.daily.co/test"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            await create_daily_room()

            call_args = mock_session.post.call_args
            headers = call_args.kwargs.get("headers", {})

            assert "Authorization" in headers
            assert "Bearer" in headers["Authorization"]
            assert "test-daily-key-123" in headers["Authorization"]

    @pytest.mark.asyncio
    async def test_raises_error_if_api_key_not_set(self, mock_settings):
        """Test that ValueError is raised if DAILY_API_KEY not set."""
        mock_settings.daily_api_key = ""

        with pytest.raises(ValueError, match="DAILY_API_KEY not set"):
            await create_daily_room()

    @pytest.mark.asyncio
    async def test_raises_error_if_api_key_none(self, mock_settings):
        """Test that ValueError is raised if DAILY_API_KEY is None."""
        mock_settings.daily_api_key = None

        with pytest.raises(ValueError, match="DAILY_API_KEY not set"):
            await create_daily_room()

    @pytest.mark.asyncio
    async def test_raises_runtime_error_on_failed_response(self, mock_settings):
        """Test that RuntimeError is raised on API failure."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.text = AsyncMock(return_value="Bad request")

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with pytest.raises(RuntimeError, match="Failed to create room"):
                await create_daily_room()

    @pytest.mark.asyncio
    async def test_handles_various_error_status_codes(self, mock_settings):
        """Test handling of various HTTP error status codes."""
        error_codes = [400, 401, 403, 500, 502, 503]

        for status_code in error_codes:
            with patch("aiohttp.ClientSession") as mock_session_class:
                mock_response = AsyncMock()
                mock_response.status = status_code
                mock_response.text = AsyncMock(return_value=f"Error {status_code}")

                mock_session = AsyncMock()
                mock_session.post = AsyncMock()
                mock_session.post.return_value.__aenter__ = AsyncMock(
                    return_value=mock_response
                )
                mock_session.post.return_value.__aexit__ = AsyncMock(
                    return_value=None
                )
                mock_session.__aenter__ = AsyncMock(return_value=mock_session)
                mock_session.__aexit__ = AsyncMock(return_value=None)
                mock_session_class.return_value = mock_session

                with pytest.raises(RuntimeError):
                    await create_daily_room()

    @pytest.mark.asyncio
    async def test_extracts_url_from_response(self, mock_settings):
        """Test that URL is extracted from response JSON."""
        expected_url = "https://medvoice.daily.co/abc123def456"

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": expected_url}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            result = await create_daily_room()

            assert result == expected_url


class TestCreateDailyRoomIntegration:
    """Test room creation in realistic scenarios."""

    @pytest.mark.asyncio
    async def test_creates_temporary_room(self, mock_settings):
        """Test creating a temporary room for a conversation."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://medvoice.daily.co/temp-room"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            result = await create_daily_room(expiry_seconds=3600)

            assert "daily.co" in result or result == "https://medvoice.daily.co/temp-room"

    @pytest.mark.asyncio
    async def test_medical_intake_session_duration(self, mock_settings):
        """Test creating room for typical medical intake duration."""
        # Typical intake might be 15-30 minutes = 900-1800 seconds
        session_duration = 1800

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://medvoice.daily.co/intake-room"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with patch("time.time", return_value=1000):
                await create_daily_room(expiry_seconds=session_duration)

                call_args = mock_session.post.call_args
                json_data = call_args.kwargs.get("json", {})
                exp_value = json_data.get("properties", {}).get("exp")

                assert exp_value == int(1000 + session_duration)


class TestCreateDailyRoomEdgeCases:
    """Test edge cases for room creation."""

    @pytest.mark.asyncio
    async def test_zero_expiry_seconds(self, mock_settings):
        """Test with zero expiry seconds."""
        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://example.daily.co/test"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with patch("time.time", return_value=1000):
                await create_daily_room(expiry_seconds=0)

                call_args = mock_session.post.call_args
                json_data = call_args.kwargs.get("json", {})
                exp_value = json_data.get("properties", {}).get("exp")

                assert exp_value == int(1000)

    @pytest.mark.asyncio
    async def test_very_large_expiry_seconds(self, mock_settings):
        """Test with very large expiry time."""
        very_large_expiry = 31536000  # 1 year in seconds

        with patch("aiohttp.ClientSession") as mock_session_class:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"url": "https://example.daily.co/test"}
            )

            mock_session = AsyncMock()
            mock_session.post = AsyncMock()
            mock_session.post.return_value.__aenter__ = AsyncMock(
                return_value=mock_response
            )
            mock_session.post.return_value.__aexit__ = AsyncMock(
                return_value=None
            )
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session

            with patch("time.time", return_value=1000):
                await create_daily_room(expiry_seconds=very_large_expiry)

                call_args = mock_session.post.call_args
                json_data = call_args.kwargs.get("json", {})
                exp_value = json_data.get("properties", {}).get("exp")

                assert exp_value == int(1000 + very_large_expiry)
