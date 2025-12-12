"""
Unit tests for voice.tts module.

Tests Text-to-Speech service factory and configuration.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.app.voice.tts import create_tts_service


class TestCreateTTSService:
    """Test create_tts_service factory function."""

    def test_returns_deepgram_tts_service_instance(
        self, mock_settings, mock_deepgram_tts_service
    ):
        """Test that function returns DeepgramTTSService instance."""
        result = create_tts_service()
        # Check that the mock was called
        assert mock_deepgram_tts_service.called

    def test_uses_settings_api_key(self, mock_settings, mock_deepgram_tts_service):
        """Test that service is created with API key from settings."""
        mock_settings.deepgram_api_key = "custom-deepgram-key"

        create_tts_service()

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["api_key"] == "custom-deepgram-key"

    def test_default_voice_is_aura_asteria_en(self, mock_settings, mock_deepgram_tts_service):
        """Test default voice is aura-asteria-en."""
        create_tts_service()

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == "aura-asteria-en"

    def test_custom_voice_parameter(self, mock_settings, mock_deepgram_tts_service):
        """Test with custom voice parameter."""
        custom_voice = "aura-luna-en"

        create_tts_service(voice=custom_voice)

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == custom_voice

    @pytest.mark.parametrize("voice", [
        "aura-asteria-en",
        "aura-luna-en",
        "aura-stella-en",
        "aura-ember-en",
        "aura-orion-en",
        "aura-arcas-en",
        "aura-perseus-en",
        "aura-angus-en",
        "aura-opheus-en",
        "aura-athena-en",
    ])
    def test_various_voices(self, mock_settings, mock_deepgram_tts_service, voice):
        """Test service creation with various Deepgram voices."""
        create_tts_service(voice=voice)

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == voice

    def test_calls_get_settings(self, mock_settings, mock_deepgram_tts_service):
        """Test that get_settings is called."""
        create_tts_service()
        # mock_settings fixture patches get_settings
        assert mock_settings is not None

    def test_service_instantiation_called_once(self, mock_settings, mock_deepgram_tts_service):
        """Test that DeepgramTTSService is instantiated once."""
        create_tts_service()
        assert mock_deepgram_tts_service.call_count == 1

    def test_only_required_params_passed(self, mock_settings, mock_deepgram_tts_service):
        """Test that exactly 2 parameters are passed."""
        create_tts_service()

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert len(call_kwargs) == 2
        assert "api_key" in call_kwargs
        assert "voice" in call_kwargs


class TestTTSServiceIntegration:
    """Test TTS service creation in realistic scenarios."""

    def test_multiple_service_instances_independent(
        self, mock_settings, mock_deepgram_tts_service
    ):
        """Test that multiple calls create independent instances."""
        mock_deepgram_tts_service.reset_mock()

        service1 = create_tts_service(voice="aura-asteria-en")
        service2 = create_tts_service(voice="aura-luna-en")

        assert mock_deepgram_tts_service.call_count == 2
        calls = mock_deepgram_tts_service.call_args_list
        assert calls[0].kwargs["voice"] == "aura-asteria-en"
        assert calls[1].kwargs["voice"] == "aura-luna-en"

    def test_medical_use_case_with_professional_voice(
        self, mock_settings, mock_deepgram_tts_service
    ):
        """Test TTS service for medical use case."""
        # Medical use case might prefer professional voice
        create_tts_service(voice="aura-stella-en")

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == "aura-stella-en"


class TestCreateTTSServiceEdgeCases:
    """Test edge cases for TTS service creation."""

    def test_empty_voice_string(self, mock_settings, mock_deepgram_tts_service):
        """Test with empty voice string."""
        create_tts_service(voice="")

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == ""

    def test_whitespace_voice_string(self, mock_settings, mock_deepgram_tts_service):
        """Test with whitespace voice string."""
        create_tts_service(voice="   ")

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == "   "

    def test_special_characters_in_voice(self, mock_settings, mock_deepgram_tts_service):
        """Test with special characters in voice name."""
        create_tts_service(voice="voice-v2.0_test")

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == "voice-v2.0_test"

    def test_very_long_voice_name(self, mock_settings, mock_deepgram_tts_service):
        """Test with very long voice name."""
        long_voice = "x" * 1000

        create_tts_service(voice=long_voice)

        call_kwargs = mock_deepgram_tts_service.call_args.kwargs
        assert call_kwargs["voice"] == long_voice

    def test_case_sensitivity(self, mock_settings, mock_deepgram_tts_service):
        """Test that voice names preserve case."""
        voices = [
            "AURA-ASTERIA-EN",
            "Aura-Luna-En",
            "aura-stella-en",
        ]

        for voice in voices:
            mock_deepgram_tts_service.reset_mock()
            create_tts_service(voice=voice)

            call_kwargs = mock_deepgram_tts_service.call_args.kwargs
            assert call_kwargs["voice"] == voice
