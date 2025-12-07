"""
MedVoice API Routes

FastAPI route definitions for sessions, chat, and voice endpoints.
"""

from fastapi import APIRouter

from .chat import router as chat_router
from .sessions import router as sessions_router
from .voice import router as voice_router

# Main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(sessions_router, tags=["sessions"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(voice_router, tags=["voice"])

__all__ = ["api_router"]
