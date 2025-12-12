"""
Speech-to-Text Service Factory

Creates Deepgram STT service for voice pipeline.
"""

from pipecat.services.deepgram.stt import DeepgramSTTService

from backend.app.config import get_settings


def create_stt_service(
    model: str = "nova-2-general",
    language: str = "en-US",
) -> DeepgramSTTService:
    """
    Create a Deepgram STT service.

    Args:
        model: Deepgram model name.
        language: Language code for recognition.

    Returns:
        Configured DeepgramSTTService instance.
    """
    settings = get_settings()
    return DeepgramSTTService(
        api_key=settings.deepgram_api_key,
        model=model,
        language=language,
    )
