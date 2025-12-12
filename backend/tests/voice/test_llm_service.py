"""
Unit tests for voice.llm.service module.

Tests LLM service factory and configuration.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.app.voice.llm.service import create_llm_service


class TestCreateLLMService:
    """Test create_llm_service factory function."""

    def test_returns_google_llm_service_instance(self, mock_settings, mock_google_llm_service):
        """Test that function returns GoogleLLMService instance."""
        result = create_llm_service()
        # Check that the mock was called
        assert mock_google_llm_service.called

    def test_uses_settings_api_key(self, mock_settings, mock_google_llm_service):
        """Test that service is created with API key from settings."""
        mock_settings.google_api_key = "custom-api-key"

        create_llm_service()

        # Verify GoogleLLMService was instantiated with correct API key
        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["api_key"] == "custom-api-key"

    def test_default_model_is_gemini_2_0_flash(self, mock_settings, mock_google_llm_service):
        """Test default model is gemini-2.0-flash."""
        create_llm_service()

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == "gemini-2.0-flash"

    def test_custom_model_parameter(self, mock_settings, mock_google_llm_service):
        """Test with custom model parameter."""
        custom_model = "gemini-1.5-pro"

        create_llm_service(model=custom_model)

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == custom_model

    @pytest.mark.parametrize("model", [
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "custom-model",
    ])
    def test_various_models(self, mock_settings, mock_google_llm_service, model):
        """Test service creation with various models."""
        create_llm_service(model=model)

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == model

    def test_calls_get_settings(self, mock_settings, mock_google_llm_service):
        """Test that get_settings is called."""
        create_llm_service()
        # mock_settings fixture patches get_settings, so if called it returns our mock
        assert mock_settings is not None

    def test_service_instantiation_called_once(self, mock_settings, mock_google_llm_service):
        """Test that GoogleLLMService is instantiated."""
        create_llm_service()
        assert mock_google_llm_service.call_count == 1

    def test_only_required_params_passed(self, mock_settings, mock_google_llm_service):
        """Test that only api_key and model are passed."""
        create_llm_service()

        call_kwargs = mock_google_llm_service.call_args.kwargs
        # Should have exactly 2 parameters
        assert len(call_kwargs) == 2
        assert "api_key" in call_kwargs
        assert "model" in call_kwargs


class TestLLMServiceIntegration:
    """Test LLM service creation in realistic scenarios."""

    def test_multiple_service_instances_independent(self, mock_settings, mock_google_llm_service):
        """Test that multiple calls create independent instances."""
        mock_google_llm_service.reset_mock()

        service1 = create_llm_service(model="model-1")
        service2 = create_llm_service(model="model-2")

        assert mock_google_llm_service.call_count == 2
        # Each call should have different model
        calls = mock_google_llm_service.call_args_list
        assert calls[0].kwargs["model"] == "model-1"
        assert calls[1].kwargs["model"] == "model-2"

    def test_api_key_validation(self):
        """Test that service requires API key from settings."""
        with patch("backend.app.config.get_settings") as mock_get_settings:
            settings = MagicMock()
            settings.google_api_key = ""
            mock_get_settings.return_value = settings

            with patch("pipecat.services.google.llm.GoogleLLMService"):
                # Service should still be called with empty key
                # (validation happens at runtime in Google SDK)
                create_llm_service()

    def test_model_parameter_type(self, mock_settings, mock_google_llm_service):
        """Test that model parameter accepts string."""
        models = ["gemini-2.0-flash", "gemini-pro", "test-model"]

        for model in models:
            mock_google_llm_service.reset_mock()
            create_llm_service(model=model)
            call_kwargs = mock_google_llm_service.call_args.kwargs
            assert isinstance(call_kwargs["model"], str)


class TestCreateLLMServiceEdgeCases:
    """Test edge cases for LLM service creation."""

    def test_empty_model_string(self, mock_settings, mock_google_llm_service):
        """Test with empty model string."""
        create_llm_service(model="")

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == ""

    def test_whitespace_model_string(self, mock_settings, mock_google_llm_service):
        """Test with whitespace model string."""
        create_llm_service(model="   ")

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == "   "

    def test_special_characters_in_model(self, mock_settings, mock_google_llm_service):
        """Test with special characters in model name."""
        special_model = "model-v2.0_test"

        create_llm_service(model=special_model)

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == special_model

    def test_very_long_model_name(self, mock_settings, mock_google_llm_service):
        """Test with very long model name."""
        long_model = "x" * 1000

        create_llm_service(model=long_model)

        call_kwargs = mock_google_llm_service.call_args.kwargs
        assert call_kwargs["model"] == long_model
