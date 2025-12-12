"""
Session Management Routes

Endpoints for creating, retrieving, and managing voice sessions.
"""

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from backend.app.models.messages import (
    SessionResponse,
    SessionState,
    SessionStatus,
)
from backend.app.services.bot_runner import (
    start_bot_for_session,
    stop_bot_for_session,
    get_active_bot_count,
)
from backend.app.services.session_store import session_store
from backend.app.voice.room import create_daily_room

router = APIRouter()


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new voice session",
)
async def create_session() -> SessionResponse:
    """
    Create a new voice intake session.

    Creates a Daily.co room and initializes session state.

    Returns:
        SessionResponse with session_id and room_url.

    Raises:
        HTTPException 503: If Daily.co room creation fails.
    """
    try:
        room_url = await create_daily_room()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Daily.co not configured: {e}",
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to create room: {e}",
        )

    session = await session_store.create(room_url=room_url)

    # Start bot in background
    try:
        await start_bot_for_session(session.session_id, room_url)
        logger.info(f"Bot started for session {session.session_id}")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        # Continue anyway - bot can be started manually if needed

    return SessionResponse(
        session_id=session.session_id,
        room_url=room_url,
        token=None,  # Public room for MVP
        status=session.status,
    )


@router.get(
    "/{session_id}",
    response_model=SessionState,
    summary="Get session state",
)
async def get_session(session_id: str) -> SessionState:
    """
    Retrieve current session state.

    Args:
        session_id: Session identifier.

    Returns:
        Full SessionState including conversation history.

    Raises:
        HTTPException 404: If session not found.
    """
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return session


@router.get(
    "/{session_id}/room",
    response_model=dict,
    summary="Get room connection info",
)
async def get_room_info(session_id: str) -> dict:
    """
    Get Daily.co room connection details for a session.

    Args:
        session_id: Session identifier.

    Returns:
        Room URL and optional token.

    Raises:
        HTTPException 404: If session not found.
    """
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    room_url = await session_store.get_room_url(session_id)
    token = await session_store.get_token(session_id)

    return {
        "room_url": room_url,
        "token": token,
    }


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End a session",
)
async def end_session(session_id: str) -> None:
    """
    End and cleanup a session.

    Args:
        session_id: Session identifier.

    Raises:
        HTTPException 404: If session not found.
    """
    session = await session_store.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )

    # Stop bot if running
    await stop_bot_for_session(session_id)

    # Mark as complete before deletion
    await session_store.update(session_id, status=SessionStatus.COMPLETE)
    await session_store.delete(session_id)


@router.patch(
    "/{session_id}/status",
    response_model=SessionState,
    summary="Update session status",
)
async def update_session_status(
    session_id: str,
    status: SessionStatus,
) -> SessionState:
    """
    Update session status.

    Args:
        session_id: Session identifier.
        status: New status value.

    Returns:
        Updated SessionState.

    Raises:
        HTTPException 404: If session not found.
    """
    session = await session_store.update(session_id, status=status)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return session
