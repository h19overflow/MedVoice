"""
In-Memory Session Store

Thread-safe session storage for demo purposes.
No database required - sessions are ephemeral.
"""

import asyncio
from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.app.models.messages import SessionState, SessionStatus, IntakeState


class SessionStore:
    """
    In-memory session storage with thread-safe operations.

    Stores sessions as Dict[session_id, SessionState].
    Sessions are ephemeral and lost on restart.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._room_urls: dict[str, str] = {}  # session_id -> room_url
        self._tokens: dict[str, str] = {}  # session_id -> token
        self._lock = asyncio.Lock()

    async def create(self, room_url: str, token: str | None = None) -> SessionState:
        """
        Create a new session.

        Args:
            room_url: Daily.co room URL for this session.
            token: Optional meeting token for authentication.

        Returns:
            Created SessionState.
        """
        async with self._lock:
            session_id = str(uuid4())
            session = SessionState(
                session_id=session_id,
                status=SessionStatus.ACTIVE,
                current_state=IntakeState.GREETING,
                turns=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self._sessions[session_id] = session
            self._room_urls[session_id] = room_url
            if token:
                self._tokens[session_id] = token
            return session

    async def get(self, session_id: str) -> SessionState | None:
        """
        Get session by ID.

        Args:
            session_id: Session identifier.

        Returns:
            SessionState if found, None otherwise.
        """
        return self._sessions.get(session_id)

    async def get_room_url(self, session_id: str) -> str | None:
        """Get Daily room URL for session."""
        return self._room_urls.get(session_id)

    async def get_token(self, session_id: str) -> str | None:
        """Get meeting token for session."""
        return self._tokens.get(session_id)

    async def update(self, session_id: str, **kwargs: Any) -> SessionState | None:
        """
        Update session fields.

        Args:
            session_id: Session identifier.
            **kwargs: Fields to update.

        Returns:
            Updated SessionState if found, None otherwise.
        """
        async with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None

            # Update allowed fields
            update_data = session.model_dump()
            for key, value in kwargs.items():
                if key in update_data:
                    update_data[key] = value
            update_data["updated_at"] = datetime.utcnow()

            updated_session = SessionState(**update_data)
            self._sessions[session_id] = updated_session
            return updated_session

    async def delete(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier.

        Returns:
            True if deleted, False if not found.
        """
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                self._room_urls.pop(session_id, None)
                self._tokens.pop(session_id, None)
                return True
            return False

    async def cleanup_all(self) -> int:
        """
        Delete all sessions.

        Returns:
            Number of sessions deleted.
        """
        async with self._lock:
            count = len(self._sessions)
            self._sessions.clear()
            self._room_urls.clear()
            self._tokens.clear()
            return count

    async def list_active(self) -> list[SessionState]:
        """List all active sessions."""
        return [
            s for s in self._sessions.values()
            if s.status == SessionStatus.ACTIVE
        ]

    def __len__(self) -> int:
        """Return number of sessions."""
        return len(self._sessions)


# Global session store instance
session_store = SessionStore()
