"""
Message and Session Models

Pydantic schemas for chat messages, conversation turns, and session state.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    COMPLETE = "complete"
    ABANDONED = "abandoned"


class IntakeState(str, Enum):
    """Intake flow state machine states."""

    GREETING = "GREETING"
    DEMOGRAPHICS = "DEMOGRAPHICS"
    VISIT_REASON = "VISIT_REASON"
    MEDICAL_HISTORY = "MEDICAL_HISTORY"
    MEDICATIONS = "MEDICATIONS"
    ALLERGIES = "ALLERGIES"
    CONFIRMATION = "CONFIRMATION"
    COMPLETE = "COMPLETE"


class ChatMessage(BaseModel):
    """Single chat message."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationTurn(BaseModel):
    """Single conversation turn with metadata."""

    turn_id: int
    speaker: str  # "agent" or "patient"
    text: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state: IntakeState
    extracted: Optional[dict[str, Any]] = None


class SessionState(BaseModel):
    """Current session state."""

    session_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    current_state: IntakeState = IntakeState.GREETING
    turns: list[ConversationTurn] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CreateSessionResponse(BaseModel):
    """Response for session creation."""

    session_id: str
    daily_room_url: Optional[str] = None
    token: Optional[str] = None


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str


class ChatResponse(BaseModel):
    """Response for chat endpoint."""

    response: str
    state: IntakeState
    is_complete: bool = False
