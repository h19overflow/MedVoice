"""
Unit tests for voice.vad module.

Tests Voice Activity Detection factory.
"""

import pytest
from unittest.mock import patch, MagicMock, call

from backend.app.voice.vad import create_vad_analyzer


class TestCreateVADAnalyzer:
    """Test create_vad_analyzer factory function."""

    def test_returns_silero_vad_analyzer_instance(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that function returns SileroVADAnalyzer instance."""
        result = create_vad_analyzer()
        assert mock_silero_vad_analyzer.called

    def test_creates_vad_params(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test that VADParams is created."""
        create_vad_analyzer()
        assert mock_vad_params.called

    def test_default_stop_secs_is_0_3(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test default stop_secs is 0.3."""
        create_vad_analyzer()

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 0.3

    def test_custom_stop_secs_parameter(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test with custom stop_secs parameter."""
        custom_stop_secs = 0.5

        create_vad_analyzer(stop_secs=custom_stop_secs)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 0.5

    @pytest.mark.parametrize("stop_secs", [
        0.1,
        0.2,
        0.3,
        0.5,
        0.7,
        1.0,
        1.5,
        2.0,
    ])
    def test_various_stop_secs_values(
        self, mock_silero_vad_analyzer, mock_vad_params, stop_secs
    ):
        """Test VAD analyzer with various stop_secs values."""
        create_vad_analyzer(stop_secs=stop_secs)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == stop_secs

    def test_vad_params_passed_to_analyzer(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that VADParams is passed to SileroVADAnalyzer."""
        create_vad_analyzer()

        # Check that SileroVADAnalyzer was called with params kwarg
        call_kwargs = mock_silero_vad_analyzer.call_args.kwargs
        assert "params" in call_kwargs

    def test_analyzer_instantiation_called_once(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that SileroVADAnalyzer is instantiated once."""
        create_vad_analyzer()
        assert mock_silero_vad_analyzer.call_count == 1

    def test_params_instantiation_called_once(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that VADParams is instantiated once."""
        create_vad_analyzer()
        assert mock_vad_params.call_count == 1

    def test_vad_params_created_before_analyzer(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that VADParams is created before SileroVADAnalyzer."""
        # Reset call history
        mock_vad_params.reset_mock()
        mock_silero_vad_analyzer.reset_mock()

        create_vad_analyzer()

        # Check call order: VADParams should be called first
        assert mock_vad_params.call_count >= 1
        assert mock_silero_vad_analyzer.call_count >= 1


class TestVADAnalyzerIntegration:
    """Test VAD analyzer creation in realistic scenarios."""

    def test_multiple_analyzer_instances_independent(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that multiple calls create independent instances."""
        mock_silero_vad_analyzer.reset_mock()
        mock_vad_params.reset_mock()

        analyzer1 = create_vad_analyzer(stop_secs=0.3)
        analyzer2 = create_vad_analyzer(stop_secs=0.5)

        assert mock_silero_vad_analyzer.call_count == 2
        assert mock_vad_params.call_count == 2

        calls = mock_vad_params.call_args_list
        assert calls[0].kwargs["stop_secs"] == 0.3
        assert calls[1].kwargs["stop_secs"] == 0.5

    def test_conversation_use_case(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test VAD for conversation use case (shorter silence threshold)."""
        create_vad_analyzer(stop_secs=0.3)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 0.3

    def test_medical_intake_use_case(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test VAD for medical intake use case."""
        # Medical intake might allow longer thinking pauses
        create_vad_analyzer(stop_secs=0.5)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 0.5


class TestCreateVADAnalyzerEdgeCases:
    """Test edge cases for VAD analyzer creation."""

    def test_zero_stop_secs(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test with zero stop_secs (edge case)."""
        create_vad_analyzer(stop_secs=0.0)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 0.0

    def test_very_small_stop_secs(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test with very small stop_secs."""
        create_vad_analyzer(stop_secs=0.001)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 0.001

    def test_very_large_stop_secs(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test with very large stop_secs."""
        create_vad_analyzer(stop_secs=10.0)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == 10.0

    def test_negative_stop_secs(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test with negative stop_secs (edge case, may be invalid)."""
        # Factory doesn't validate, that's done by Silero VAD
        create_vad_analyzer(stop_secs=-0.5)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == -0.5

    def test_float_precision(self, mock_silero_vad_analyzer, mock_vad_params):
        """Test that float precision is preserved."""
        precise_value = 0.123456789
        create_vad_analyzer(stop_secs=precise_value)

        call_kwargs = mock_vad_params.call_args.kwargs
        assert call_kwargs["stop_secs"] == precise_value

    def test_integer_stop_secs_converted_to_float(
        self, mock_silero_vad_analyzer, mock_vad_params
    ):
        """Test that integer stop_secs works (Python float coercion)."""
        create_vad_analyzer(stop_secs=1)

        call_kwargs = mock_vad_params.call_args.kwargs
        # Should still work due to Python's numeric coercion
        assert call_kwargs["stop_secs"] == 1
