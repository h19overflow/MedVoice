"""
MedVoice Services

Business logic for session management and intake processing.
"""

from .session_store import SessionStore, session_store

__all__ = [
    "SessionStore",
    "session_store",
]

# Lazy imports for modules with heavy dependencies
def get_bot_runner():
    """Get bot runner module (lazy load to avoid pipecat import at startup)."""
    from . import bot_runner
    return bot_runner

def get_intake_extractor():
    """Get intake extractor module."""
    from . import intake_extractor
    return intake_extractor
