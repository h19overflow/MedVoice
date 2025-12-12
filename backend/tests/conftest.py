"""
Shared test fixtures and configuration for all tests.

Provides mocked external services and test utilities.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch("backend.app.config.get_settings") as mock:
        settings = MagicMock()
        settings.deepgram_api_key = "test-deepgram-key"
        settings.google_api_key = "test-google-key"
        settings.daily_api_key = "test-daily-key"
        mock.return_value = settings
        yield settings


@pytest.fixture
def mock_google_llm_service():
    """Mock GoogleLLMService."""
    with patch("pipecat.services.google.llm.GoogleLLMService") as mock:
        service = MagicMock()
        service.api_key = "test-key"
        service.model = "gemini-2.0-flash"
        mock.return_value = service
        yield service


@pytest.fixture
def mock_deepgram_stt_service():
    """Mock DeepgramSTTService."""
    with patch("pipecat.services.deepgram.stt.DeepgramSTTService") as mock:
        service = MagicMock()
        service.api_key = "test-key"
        service.model = "nova-2-general"
        service.language = "en-US"
        mock.return_value = service
        yield service


@pytest.fixture
def mock_deepgram_tts_service():
    """Mock DeepgramTTSService."""
    with patch("pipecat.services.deepgram.tts.DeepgramTTSService") as mock:
        service = MagicMock()
        service.api_key = "test-key"
        service.voice = "aura-asteria-en"
        mock.return_value = service
        yield service


@pytest.fixture
def mock_silero_vad_analyzer():
    """Mock SileroVADAnalyzer."""
    with patch("pipecat.audio.vad.silero.SileroVADAnalyzer") as mock:
        analyzer = MagicMock()
        analyzer.params = MagicMock(stop_secs=0.3)
        mock.return_value = analyzer
        yield analyzer


@pytest.fixture
def mock_vad_params():
    """Mock VADParams."""
    with patch("pipecat.audio.vad.vad_analyzer.VADParams") as mock:
        params = MagicMock()
        params.stop_secs = 0.3
        mock.return_value = params
        yield params


@pytest.fixture
def mock_daily_transport():
    """Mock DailyTransport."""
    with patch("pipecat.transports.daily.transport.DailyTransport") as mock:
        transport = MagicMock()
        transport.room_url = "https://example.daily.co/test-room"
        transport.bot_name = "MedVoice"
        transport.input = MagicMock()
        transport.output = MagicMock()
        transport.event_handler = MagicMock()
        mock.return_value = transport
        yield transport


@pytest.fixture
def mock_daily_params():
    """Mock DailyParams."""
    with patch("pipecat.transports.daily.transport.DailyParams") as mock:
        params = MagicMock()
        params.audio_in_enabled = True
        params.audio_out_enabled = True
        params.vad_enabled = True
        mock.return_value = params
        yield params


@pytest.fixture
def mock_openai_llm_context():
    """Mock OpenAILLMContext."""
    with patch("pipecat.processors.aggregators.openai_llm_context.OpenAILLMContext") as mock:
        context = MagicMock()
        context.messages = []
        mock.return_value = context
        yield context


@pytest.fixture
async def mock_aiohttp_session():
    """Mock aiohttp ClientSession for async tests."""
    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = AsyncMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session
        mock_session_class.return_value.__aexit__.return_value = None
        yield mock_session
