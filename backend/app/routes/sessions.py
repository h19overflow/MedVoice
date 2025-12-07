"""
Sessions Route

Handles session creation, status, and results retrieval.
"""

from fastapi import APIRouter, HTTPException

from ..models.intake import IntakeData
from ..models.messages import CreateSessionResponse, SessionState
from ..services.intake import create_session, delete_session, get_session

router = APIRouter()


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_intake_session() -> CreateSessionResponse:
    """
    Create a new intake session.

    Returns session ID and optionally Daily.co room URL for voice mode.
    """
    service = create_session()

    # TODO: Create Daily.co room for voice sessions
    # For now, return just the session ID

    return CreateSessionResponse(
        session_id=service.session_id,
        daily_room_url=None,  # Will be populated when voice is implemented
        token=None,
    )


@router.get("/sessions/{session_id}", response_model=SessionState)
async def get_session_status(session_id: str) -> SessionState:
    """
    Get current session state and progress.
    """
    service = get_session(session_id)
    if not service:
        raise HTTPException(status_code=404, detail="Session not found")

    return service.get_session_state()


@router.get("/sessions/{session_id}/results", response_model=IntakeData)
async def get_session_results(session_id: str) -> IntakeData:
    """
    Get the extracted intake data for a session.
    """
    service = get_session(session_id)
    if not service:
        raise HTTPException(status_code=404, detail="Session not found")

    return service.get_intake_data()


@router.delete("/sessions/{session_id}")
async def end_session(session_id: str) -> dict:
    """
    End and delete a session.
    """
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"status": "deleted", "session_id": session_id}
