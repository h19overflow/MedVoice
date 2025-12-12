"""
MedVoice Voice Pipeline

Pipecat-based voice processing for real-time audio conversations.

Note: Heavy imports (pipecat, etc.) are lazy-loaded to avoid import errors
when dependencies aren't installed. Use direct imports for specific modules.
"""

# Only import room.py here as it has minimal dependencies
from backend.app.voice.room import create_daily_room

__all__ = [
    "create_daily_room",
]


def get_voice_components():
    """
    Lazy-load voice pipeline components.

    Returns dict with all voice component factories.
    Only call this when pipecat is installed.
    """
    from backend.app.voice.context import create_context
    from backend.app.voice.llm import create_llm_service
    from backend.app.voice.pipeline_flow import run_voice_bot
    from backend.app.voice.stt import create_stt_service
    from backend.app.voice.transport import create_transport
    from backend.app.voice.tts import create_tts_service
    from backend.app.voice.vad import create_vad_analyzer

    return {
        "create_context": create_context,
        "create_llm_service": create_llm_service,
        "create_stt_service": create_stt_service,
        "create_transport": create_transport,
        "create_tts_service": create_tts_service,
        "create_vad_analyzer": create_vad_analyzer,
        "run_voice_bot": run_voice_bot,
    }
