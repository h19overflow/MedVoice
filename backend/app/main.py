"""
MedVoice FastAPI Application

Main entry point for the voice intake backend.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.app.routes import api_router
from backend.app.services.session_store import session_store


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown tasks.
    """
    # Startup
    settings = get_settings()
    print(f"Starting MedVoice API (debug={settings.debug})")
    yield
    # Shutdown
    count = await session_store.cleanup_all()
    print(f"Cleaned up {count} sessions")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="MedVoice API",
        description="Voice-first medical intake assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware - allow all origins in development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "medvoice-api",
        }

    return app


# Application instance
app = create_app()
