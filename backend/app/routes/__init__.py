"""
MedVoice API Routes

FastAPI route definitions for session management.
"""

from fastapi import APIRouter

from .sessions import router as sessions_router

# Main API router
api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])

__all__ = ["api_router"]
