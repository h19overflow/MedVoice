"""
Shared test fixtures and configuration for all tests.

Provides mocked external services and test utilities.
"""

import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Mock pipecat module and all its submodules before any imports
sys.modules["pipecat"] = MagicMock()
sys.modules["pipecat.services"] = MagicMock()
sys.modules["pipecat.services.google"] = MagicMock()
sys.modules["pipecat.services.google.llm"] = MagicMock()
sys.modules["pipecat.services.deepgram"] = MagicMock()
sys.modules["pipecat.services.deepgram.stt"] = MagicMock()
sys.modules["pipecat.services.deepgram.tts"] = MagicMock()
sys.modules["pipecat.audio"] = MagicMock()
sys.modules["pipecat.audio.vad"] = MagicMock()
sys.modules["pipecat.audio.vad.silero"] = MagicMock()
sys.modules["pipecat.audio.vad.vad_analyzer"] = MagicMock()
sys.modules["pipecat.processors"] = MagicMock()
sys.modules["pipecat.processors.aggregators"] = MagicMock()
sys.modules["pipecat.processors.aggregators.openai_llm_context"] = MagicMock()
sys.modules["pipecat.transports"] = MagicMock()
sys.modules["pipecat.transports.daily"] = MagicMock()
sys.modules["pipecat.transports.daily.transport"] = MagicMock()
sys.modules["pipecat.frames"] = MagicMock()
sys.modules["pipecat.frames.frames"] = MagicMock()
sys.modules["pipecat.pipeline"] = MagicMock()
sys.modules["pipecat.pipeline.pipeline"] = MagicMock()
sys.modules["pipecat.pipeline.runner"] = MagicMock()
sys.modules["pipecat.pipeline.task"] = MagicMock()

# Mock aiohttp for async tests
sys.modules["aiohttp"] = MagicMock()


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch("backend.app.config.get_settings") as mock_get_settings:
        with patch("backend.app.config.Settings") as mock_settings_class:
            settings = MagicMock()
            settings.deepgram_api_key = "test-deepgram-key"
            settings.google_api_key = "test-google-key"
            settings.daily_api_key = "test-daily-key"
            mock_get_settings.return_value = settings
            mock_settings_class.return_value = settings
            yield settings


@pytest.fixture
def mock_google_llm_service():
    """Mock GoogleLLMService."""
    with patch("backend.app.voice.llm.service.GoogleLLMService") as mock:
        service = MagicMock()
        service.api_key = "test-key"
        service.model = "gemini-2.0-flash"
        mock.return_value = service
        yield mock


@pytest.fixture
def mock_deepgram_stt_service():
    """Mock DeepgramSTTService."""
    with patch("backend.app.voice.stt.DeepgramSTTService") as mock:
        service = MagicMock()
        service.api_key = "test-key"
        service.model = "nova-2-general"
        service.language = "en-US"
        mock.return_value = service
        yield mock


@pytest.fixture
def mock_deepgram_tts_service():
    """Mock DeepgramTTSService."""
    with patch("backend.app.voice.tts.DeepgramTTSService") as mock:
        service = MagicMock()
        service.api_key = "test-key"
        service.voice = "aura-asteria-en"
        mock.return_value = service
        yield mock


@pytest.fixture
def mock_silero_vad_analyzer():
    """Mock SileroVADAnalyzer."""
    with patch("backend.app.voice.vad.SileroVADAnalyzer") as mock:
        analyzer = MagicMock()
        analyzer.params = MagicMock(stop_secs=0.3)
        mock.return_value = analyzer
        yield mock


@pytest.fixture
def mock_vad_params():
    """Mock VADParams."""
    with patch("backend.app.voice.vad.VADParams") as mock:
        params = MagicMock()
        params.stop_secs = 0.3
        mock.return_value = params
        yield mock


@pytest.fixture
def mock_daily_transport():
    """Mock DailyTransport."""
    with patch("backend.app.voice.transport.DailyTransport") as mock:
        transport = MagicMock()
        transport.room_url = "https://example.daily.co/test-room"
        transport.bot_name = "MedVoice"
        transport.input = MagicMock()
        transport.output = MagicMock()
        transport.event_handler = MagicMock()
        mock.return_value = transport
        yield mock


@pytest.fixture
def mock_daily_params():
    """Mock DailyParams."""
    with patch("backend.app.voice.transport.DailyParams") as mock:
        params = MagicMock()
        params.audio_in_enabled = True
        params.audio_out_enabled = True
        params.vad_enabled = True
        mock.return_value = params
        yield mock


@pytest.fixture
def mock_openai_llm_context():
    """Mock OpenAILLMContext."""
    with patch("backend.app.voice.context.OpenAILLMContext") as mock:
        context = MagicMock()
        context.messages = []
        mock.return_value = context
        yield mock


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession for async tests."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"url": "https://test.daily.co/room"})
    mock_response.text = AsyncMock(return_value="error")

    mock_session = AsyncMock()
    mock_session.post = AsyncMock()

    # Setup the async context manager for post
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    mock_session.post.return_value = mock_context

    with patch("aiohttp.ClientSession") as mock_session_class:
        # Setup the async context manager for the session
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        mock_session_class.return_value = mock_session_context

        yield mock_session
