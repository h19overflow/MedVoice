"""
Chat Route

Handles text-based chat interactions for intake.
"""

from fastapi import APIRouter, HTTPException

from ..models.messages import ChatRequest, ChatResponse
from ..services.intake import get_session

router = APIRouter()


@router.post("/sessions/{session_id}/chat", response_model=ChatResponse)
async def send_chat_message(session_id: str, request: ChatRequest) -> ChatResponse:
    """
    Send a chat message and receive agent response.

    This uses the same IntakeService as voice mode,
    ensuring consistent behavior across both interfaces.
    """
    service = get_session(session_id)
    if not service:
        raise HTTPException(status_code=404, detail="Session not found")

    # Process the message
    response = await service.process_message(request.message)

    return ChatResponse(
        response=response,
        state=service.state,
        is_complete=service.is_complete(),
    )


@router.get("/sessions/{session_id}/greeting")
async def get_greeting(session_id: str) -> dict:
    """
    Get the initial greeting to start the conversation.

    Call this after creating a session to get the first message.
    """
    service = get_session(session_id)
    if not service:
        raise HTTPException(status_code=404, detail="Session not found")

    greeting = service.get_greeting()

    return {
        "message": greeting,
        "state": service.state.value,
    }
