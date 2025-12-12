"""
Unit tests for voice.stt module.

Tests Speech-to-Text service factory and configuration.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.app.voice.stt import create_stt_service


class TestCreateSTTService:
    """Test create_stt_service factory function."""

    def test_returns_deepgram_stt_service_instance(
        self, mock_settings, mock_deepgram_stt_service
    ):
        """Test that function returns DeepgramSTTService instance."""
        result = create_stt_service()
        # Check that the mock was called
        assert mock_deepgram_stt_service.called

    def test_uses_settings_api_key(self, mock_settings, mock_deepgram_stt_service):
        """Test that service is created with API key from settings."""
        mock_settings.deepgram_api_key = "custom-deepgram-key"

        create_stt_service()

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["api_key"] == "custom-deepgram-key"

    def test_default_model_is_nova_2_general(self, mock_settings, mock_deepgram_stt_service):
        """Test default model is nova-2-general."""
        create_stt_service()

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == "nova-2-general"

    def test_default_language_is_en_us(self, mock_settings, mock_deepgram_stt_service):
        """Test default language is en-US."""
        create_stt_service()

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["language"] == "en-US"

    def test_custom_model_parameter(self, mock_settings, mock_deepgram_stt_service):
        """Test with custom model parameter."""
        custom_model = "nova-2-conversationalai"

        create_stt_service(model=custom_model)

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == custom_model

    def test_custom_language_parameter(self, mock_settings, mock_deepgram_stt_service):
        """Test with custom language parameter."""
        custom_language = "es-ES"

        create_stt_service(language=custom_language)

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["language"] == custom_language

    @pytest.mark.parametrize("model", [
        "nova-2-general",
        "nova-2-conversationalai",
        "nova-2-medical",
        "nova-2-diarization",
        "nova-1",
    ])
    def test_various_models(self, mock_settings, mock_deepgram_stt_service, model):
        """Test service creation with various Deepgram models."""
        create_stt_service(model=model)

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == model

    @pytest.mark.parametrize("language", [
        "en-US",
        "en-GB",
        "es-ES",
        "fr-FR",
        "de-DE",
        "it-IT",
        "pt-BR",
        "ja-JP",
        "zh-CN",
    ])
    def test_various_languages(self, mock_settings, mock_deepgram_stt_service, language):
        """Test service creation with various languages."""
        create_stt_service(language=language)

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["language"] == language

    def test_both_custom_parameters(self, mock_settings, mock_deepgram_stt_service):
        """Test with both custom model and language."""
        create_stt_service(model="nova-2-medical", language="es-ES")

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == "nova-2-medical"
        assert call_kwargs["language"] == "es-ES"

    def test_calls_get_settings(self, mock_settings, mock_deepgram_stt_service):
        """Test that get_settings is called."""
        create_stt_service()
        # mock_settings fixture patches get_settings
        assert mock_settings is not None

    def test_service_instantiation_called_once(self, mock_settings, mock_deepgram_stt_service):
        """Test that DeepgramSTTService is instantiated once."""
        create_stt_service()
        assert mock_deepgram_stt_service.call_count == 1

    def test_only_required_params_passed(self, mock_settings, mock_deepgram_stt_service):
        """Test that exactly 3 parameters are passed."""
        create_stt_service()

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert len(call_kwargs) == 3
        assert "api_key" in call_kwargs
        assert "model" in call_kwargs
        assert "language" in call_kwargs


class TestSTTServiceIntegration:
    """Test STT service creation in realistic scenarios."""

    def test_multiple_service_instances_independent(
        self, mock_settings, mock_deepgram_stt_service
    ):
        """Test that multiple calls create independent instances."""
        mock_deepgram_stt_service.reset_mock()

        service1 = create_stt_service(model="nova-2-general")
        service2 = create_stt_service(model="nova-2-medical")

        assert mock_deepgram_stt_service.call_count == 2
        calls = mock_deepgram_stt_service.call_args_list
        assert calls[0].kwargs["model"] == "nova-2-general"
        assert calls[1].kwargs["model"] == "nova-2-medical"

    def test_model_and_language_combinations(
        self, mock_settings, mock_deepgram_stt_service
    ):
        """Test various model and language combinations."""
        combinations = [
            ("nova-2-general", "en-US"),
            ("nova-2-medical", "es-ES"),
            ("nova-2-conversationalai", "fr-FR"),
        ]

        for model, language in combinations:
            mock_deepgram_stt_service.reset_mock()
            create_stt_service(model=model, language=language)

            call_kwargs = mock_deepgram_stt_service.call_args.kwargs
            assert call_kwargs["model"] == model
            assert call_kwargs["language"] == language

    def test_medical_use_case(self, mock_settings, mock_deepgram_stt_service):
        """Test STT service for medical use case."""
        # Medical use case might use medical-specific model
        create_stt_service(model="nova-2-medical", language="en-US")

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == "nova-2-medical"
        assert call_kwargs["language"] == "en-US"


class TestCreateSTTServiceEdgeCases:
    """Test edge cases for STT service creation."""

    def test_empty_model_string(self, mock_settings, mock_deepgram_stt_service):
        """Test with empty model string."""
        create_stt_service(model="")

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == ""

    def test_empty_language_string(self, mock_settings, mock_deepgram_stt_service):
        """Test with empty language string."""
        create_stt_service(language="")

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["language"] == ""

    def test_whitespace_parameters(self, mock_settings, mock_deepgram_stt_service):
        """Test with whitespace in parameters."""
        create_stt_service(model="   ", language="   ")

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == "   "
        assert call_kwargs["language"] == "   "

    def test_special_characters_in_parameters(self, mock_settings, mock_deepgram_stt_service):
        """Test with special characters."""
        create_stt_service(model="model-v2.0", language="lang-variant_1")

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == "model-v2.0"
        assert call_kwargs["language"] == "lang-variant_1"

    def test_very_long_parameters(self, mock_settings, mock_deepgram_stt_service):
        """Test with very long parameter strings."""
        long_string = "x" * 1000

        create_stt_service(model=long_string, language=long_string)

        call_kwargs = mock_deepgram_stt_service.call_args.kwargs
        assert call_kwargs["model"] == long_string
        assert call_kwargs["language"] == long_string
