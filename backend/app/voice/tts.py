"""
Text-to-Speech Service Factory

Creates Deepgram TTS service for voice pipeline.
"""

from pipecat.services.deepgram.tts import DeepgramTTSService

from backend.app.config import get_settings


def create_tts_service(voice: str = "aura-asteria-en") -> DeepgramTTSService:
    """
    Create a Deepgram TTS service.

    Args:
        voice: Voice identifier for synthesis.

    Returns:
        Configured DeepgramTTSService instance.
    """
    settings = get_settings()
    return DeepgramTTSService(
        api_key=settings.deepgram_api_key,
        voice=voice,
    )
