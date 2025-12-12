"""
Voice Activity Detection Factory

Creates VAD analyzer for detecting speech boundaries.
"""

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams


def create_vad_analyzer(stop_secs: float = 0.3) -> SileroVADAnalyzer:
    """
    Create a Silero VAD analyzer.

    Args:
        stop_secs: Seconds of silence before stopping detection.

    Returns:
        Configured SileroVADAnalyzer instance.
    """
    return SileroVADAnalyzer(params=VADParams(stop_secs=stop_secs))
