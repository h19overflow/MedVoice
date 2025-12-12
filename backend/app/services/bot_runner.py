"""
Bot Runner Service

Manages voice bot lifecycle for sessions.
Runs bots in background tasks and tracks their state.
"""

import asyncio
from typing import Any

from loguru import logger

from backend.app.models.messages import SessionStatus
from backend.app.services.session_store import session_store


# Global registry of active bots
_active_bots: dict[str, "BotRunner"] = {}


class BotRunner:
    """
    Manages a single voice bot instance for a session.

    Handles starting, stopping, and capturing conversation data.
    """

    def __init__(self, session_id: str, room_url: str) -> None:
        self.session_id = session_id
        self.room_url = room_url
        self.task: asyncio.Task | None = None
        self.conversation_history: list[dict] = []
        self._stopped = False

    async def start(self) -> None:
        """Start the voice bot in a background task."""
        if self.task is not None:
            logger.warning(f"Bot already running for session {self.session_id}")
            return

        self.task = asyncio.create_task(self._run_bot())
        _active_bots[self.session_id] = self
        logger.info(f"Bot started for session {self.session_id}")

    async def stop(self) -> None:
        """Stop the voice bot gracefully."""
        self._stopped = True
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        _active_bots.pop(self.session_id, None)
        logger.info(f"Bot stopped for session {self.session_id}")

    async def _run_bot(self) -> None:
        """Internal method to run the pipeline."""
        try:
            # Import here to avoid circular imports and allow lazy loading
            from backend.app.voice.runner import run_pipeline_with_timeout

            conversation = await run_pipeline_with_timeout(
                room_url=self.room_url,
                timeout_seconds=600,  # 10 minute max
                on_conversation_update=self._on_conversation_update,
                on_complete=self._on_complete,
                on_error=self._on_error,
            )

            self.conversation_history = conversation

            # Extract intake data and update session
            if conversation and not self._stopped:
                await self._extract_and_save_intake()

        except asyncio.CancelledError:
            logger.info(f"Bot cancelled for session {self.session_id}")
            await session_store.update(
                self.session_id,
                status=SessionStatus.ABANDONED,
            )
        except Exception as e:
            logger.error(f"Bot error for session {self.session_id}: {e}")
            await session_store.update(
                self.session_id,
                status=SessionStatus.ABANDONED,
            )
        finally:
            _active_bots.pop(self.session_id, None)

    def _on_conversation_update(self, history: list[dict]) -> None:
        """Callback when conversation updates."""
        self.conversation_history = history.copy()
        logger.debug(f"Conversation updated: {len(history)} messages")

    def _on_complete(self) -> None:
        """Callback when pipeline completes normally."""
        logger.info(f"Pipeline completed for session {self.session_id}")

    def _on_error(self, error: Exception) -> None:
        """Callback on pipeline error."""
        logger.error(f"Pipeline error for {self.session_id}: {error}")

    async def _extract_and_save_intake(self) -> None:
        """Extract intake data from conversation and save to session."""
        try:
            from backend.app.services.intake_extractor import extract_intake_data

            intake_data = await extract_intake_data(self.conversation_history)

            # Update session with extracted data and conversation
            await session_store.update(
                self.session_id,
                status=SessionStatus.COMPLETE,
            )

            # Store intake data in session (we'll add this field)
            logger.info(f"Intake extracted for session {self.session_id}")
            logger.debug(f"Intake data: {intake_data}")

        except Exception as e:
            logger.error(f"Intake extraction failed: {e}")
            # Still mark complete even if extraction fails
            await session_store.update(
                self.session_id,
                status=SessionStatus.COMPLETE,
            )


async def start_bot_for_session(session_id: str, room_url: str) -> BotRunner:
    """
    Start a bot for a session.

    Args:
        session_id: Session identifier.
        room_url: Daily.co room URL.

    Returns:
        BotRunner instance.
    """
    runner = BotRunner(session_id, room_url)
    await runner.start()
    return runner


async def stop_bot_for_session(session_id: str) -> bool:
    """
    Stop a bot for a session.

    Args:
        session_id: Session identifier.

    Returns:
        True if bot was stopped, False if not found.
    """
    runner = _active_bots.get(session_id)
    if runner:
        await runner.stop()
        return True
    return False


def get_active_bot(session_id: str) -> BotRunner | None:
    """Get active bot for a session."""
    return _active_bots.get(session_id)


def get_active_bot_count() -> int:
    """Get count of active bots."""
    return len(_active_bots)
