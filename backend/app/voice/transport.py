"""
WebRTC Transport Factory

Creates Daily.co transport for real-time audio streaming.
"""

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.transports.daily.transport import DailyParams, DailyTransport

from backend.app.voice.vad import create_vad_analyzer


def create_transport(
    room_url: str,
    bot_name: str = "MedVoice",
    vad_analyzer: SileroVADAnalyzer | None = None,
) -> DailyTransport:
    """
    Create a Daily WebRTC transport.

    Args:
        room_url: Daily.co room URL.
        bot_name: Display name for the bot.
        vad_analyzer: Optional custom VAD analyzer.

    Returns:
        Configured DailyTransport instance.
    """
    if vad_analyzer is None:
        vad_analyzer = create_vad_analyzer()

    return DailyTransport(
        room_url=room_url,
        token=None,
        bot_name=bot_name,
        params=DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=vad_analyzer,
        ),
    )
