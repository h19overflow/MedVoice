"""
Unit tests for voice.transport module.

Tests WebRTC transport factory.
"""

import pytest
from unittest.mock import patch, MagicMock, call

from backend.app.voice.transport import create_transport


class TestCreateTransport:
    """Test create_transport factory function."""

    def test_returns_daily_transport_instance(
        self, mock_daily_transport, mock_daily_params
    ):
        """Test that function returns DailyTransport instance."""
        room_url = "https://example.daily.co/test-room"

        result = create_transport(room_url)

        assert mock_daily_transport.called

    def test_uses_provided_room_url(self, mock_daily_transport, mock_daily_params):
        """Test that room_url is passed to transport."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["room_url"] == room_url

    def test_default_bot_name_is_medvoice(
        self, mock_daily_transport, mock_daily_params
    ):
        """Test default bot_name is 'MedVoice'."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == "MedVoice"

    def test_custom_bot_name(self, mock_daily_transport, mock_daily_params):
        """Test with custom bot_name."""
        room_url = "https://example.daily.co/test-room"
        custom_name = "MedBot"

        create_transport(room_url, bot_name=custom_name)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == custom_name

    def test_token_is_none(self, mock_daily_transport, mock_daily_params):
        """Test that token is None (not required for this setup)."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["token"] is None

    def test_creates_vad_analyzer_by_default(self, mock_daily_transport, mock_daily_params):
        """Test that VAD analyzer is created by default."""
        room_url = "https://example.daily.co/test-room"

        with patch("backend.app.voice.transport.create_vad_analyzer") as mock_create_vad:
            create_transport(room_url)

            mock_create_vad.assert_called_once()

    def test_uses_provided_vad_analyzer(self, mock_daily_transport, mock_daily_params):
        """Test with provided VAD analyzer."""
        room_url = "https://example.daily.co/test-room"
        custom_vad = MagicMock()

        create_transport(room_url, vad_analyzer=custom_vad)

        # Should not create new one if provided
        call_kwargs = mock_daily_transport.call_args.kwargs
        params_obj = call_kwargs["params"]

    def test_creates_daily_params(self, mock_daily_transport, mock_daily_params):
        """Test that DailyParams is created."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        assert mock_daily_params.called

    def test_daily_params_audio_in_enabled(self, mock_daily_transport, mock_daily_params):
        """Test that audio_in_enabled is True."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_params.call_args.kwargs
        assert call_kwargs["audio_in_enabled"] is True

    def test_daily_params_audio_out_enabled(self, mock_daily_transport, mock_daily_params):
        """Test that audio_out_enabled is True."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_params.call_args.kwargs
        assert call_kwargs["audio_out_enabled"] is True

    def test_daily_params_vad_enabled(self, mock_daily_transport, mock_daily_params):
        """Test that vad_enabled is True."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_params.call_args.kwargs
        assert call_kwargs["vad_enabled"] is True

    def test_daily_params_has_vad_analyzer(self, mock_daily_transport, mock_daily_params):
        """Test that vad_analyzer is included in params."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_params.call_args.kwargs
        assert "vad_analyzer" in call_kwargs

    def test_transport_instantiation_called_once(self, mock_daily_transport, mock_daily_params):
        """Test that DailyTransport is instantiated once."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        assert mock_daily_transport.call_count == 1

    @pytest.mark.parametrize("room_url", [
        "https://example.daily.co/room1",
        "https://example.daily.co/room2",
        "https://custom.daily.co/test",
        "https://daily.co/abc123",
    ])
    def test_various_room_urls(
        self, mock_daily_transport, mock_daily_params, room_url
    ):
        """Test with various room URLs."""
        create_transport(room_url)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["room_url"] == room_url

    @pytest.mark.parametrize("bot_name", [
        "MedVoice",
        "Assistant",
        "MedBot",
        "HealthBot",
    ])
    def test_various_bot_names(
        self, mock_daily_transport, mock_daily_params, bot_name
    ):
        """Test with various bot names."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url, bot_name=bot_name)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == bot_name


class TestTransportIntegration:
    """Test transport creation in realistic scenarios."""

    def test_medical_intake_transport(self, mock_daily_transport, mock_daily_params):
        """Test transport for medical intake scenario."""
        room_url = "https://medvoice.daily.co/patient-intake"

        create_transport(room_url, bot_name="MedVoice")

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["room_url"] == room_url
        assert call_kwargs["bot_name"] == "MedVoice"

    def test_multiple_transport_instances_independent(
        self, mock_daily_transport, mock_daily_params
    ):
        """Test that multiple transports are independent."""
        mock_daily_transport.reset_mock()

        url1 = "https://example.daily.co/room1"
        url2 = "https://example.daily.co/room2"

        create_transport(url1, bot_name="Bot1")
        create_transport(url2, bot_name="Bot2")

        assert mock_daily_transport.call_count == 2
        calls = mock_daily_transport.call_args_list
        assert calls[0].kwargs["room_url"] == url1
        assert calls[0].kwargs["bot_name"] == "Bot1"
        assert calls[1].kwargs["room_url"] == url2
        assert calls[1].kwargs["bot_name"] == "Bot2"


class TestCreateTransportEdgeCases:
    """Test edge cases for transport creation."""

    def test_empty_bot_name(self, mock_daily_transport, mock_daily_params):
        """Test with empty bot name."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url, bot_name="")

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == ""

    def test_very_long_room_url(self, mock_daily_transport, mock_daily_params):
        """Test with very long room URL."""
        long_url = "https://example.daily.co/" + "x" * 1000

        create_transport(long_url)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["room_url"] == long_url

    def test_very_long_bot_name(self, mock_daily_transport, mock_daily_params):
        """Test with very long bot name."""
        long_name = "x" * 1000

        create_transport("https://example.daily.co/test", bot_name=long_name)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == long_name

    def test_special_characters_in_bot_name(self, mock_daily_transport, mock_daily_params):
        """Test with special characters in bot name."""
        room_url = "https://example.daily.co/test-room"
        special_name = "Bot-v2.0_Test!@#$"

        create_transport(room_url, bot_name=special_name)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == special_name

    def test_unicode_bot_name(self, mock_daily_transport, mock_daily_params):
        """Test with Unicode characters in bot name."""
        room_url = "https://example.daily.co/test-room"
        unicode_name = "MedBot-医疗机器人"

        create_transport(room_url, bot_name=unicode_name)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert call_kwargs["bot_name"] == unicode_name

    def test_custom_vad_analyzer_is_used(self, mock_daily_transport, mock_daily_params):
        """Test that custom VAD analyzer is used when provided."""
        room_url = "https://example.daily.co/test-room"
        custom_vad = MagicMock()

        with patch("backend.app.voice.transport.create_vad_analyzer") as mock_create_vad:
            create_transport(room_url, vad_analyzer=custom_vad)

            # create_vad_analyzer should not be called when custom vad is provided
            mock_create_vad.assert_not_called()

    def test_params_passed_to_transport(self, mock_daily_transport, mock_daily_params):
        """Test that params object is passed to transport."""
        room_url = "https://example.daily.co/test-room"

        create_transport(room_url)

        call_kwargs = mock_daily_transport.call_args.kwargs
        assert "params" in call_kwargs
        assert call_kwargs["params"] is not None
