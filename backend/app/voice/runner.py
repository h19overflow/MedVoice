"""
Voice Pipeline Runner

Runs the Pipecat voice pipeline for a given room URL.
Designed to be called from bot_runner for session-based usage.
"""

import asyncio
from typing import Callable

from loguru import logger
from pipecat.frames.frames import EndFrame, LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask

from backend.app.voice.context import create_context
from backend.app.voice.llm import (
    create_llm_service,
    get_greeting_message,
    get_system_message,
)
from backend.app.voice.stt import create_stt_service
from backend.app.voice.transport import create_transport
from backend.app.voice.tts import create_tts_service


async def run_pipeline_for_room(
    room_url: str,
    on_conversation_update: Callable[[list[dict]], None] | None = None,
    on_complete: Callable[[], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
) -> list[dict]:
    """
    Run the voice pipeline for a specific Daily room.

    Args:
        room_url: Daily.co room URL to join.
        on_conversation_update: Callback when conversation updates.
        on_complete: Callback when pipeline completes.
        on_error: Callback on error.

    Returns:
        List of conversation messages.
    """
    conversation_history: list[dict] = []

    try:
        # Create services
        transport = create_transport(room_url, bot_name="MedVoice Bot")
        stt = create_stt_service()
        tts = create_tts_service()
        llm = create_llm_service()

        # Create context with system prompt
        context = create_context([get_system_message()])
        context_aggregator = llm.create_context_aggregator(context)

        # Build pipeline
        pipeline = Pipeline(
            [
                transport.input(),
                stt,
                context_aggregator.user(),
                llm,
                tts,
                transport.output(),
                context_aggregator.assistant(),
            ]
        )

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
            ),
        )

        # Event handlers
        @transport.event_handler("on_first_participant_joined")
        async def on_joined(transport, participant):
            logger.info(f"Participant joined: {participant['id']}")
            await task.queue_frames([LLMMessagesFrame([get_greeting_message()])])

        @transport.event_handler("on_participant_left")
        async def on_left(transport, participant, reason):
            logger.info(f"Participant left: {reason}")
            # Capture conversation from context
            if context.messages:
                conversation_history.clear()
                conversation_history.extend(
                    [{"role": m["role"], "content": m["content"]}
                     for m in context.messages if m["role"] != "system"]
                )
                if on_conversation_update:
                    on_conversation_update(conversation_history)
            await task.queue_frame(EndFrame())

        # Run pipeline
        runner = PipelineRunner()
        logger.info(f"Bot joining room: {room_url}")
        await runner.run(task)

        # Pipeline completed
        if on_complete:
            on_complete()

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        if on_error:
            on_error(e)
        raise

    return conversation_history


async def run_pipeline_with_timeout(
    room_url: str,
    timeout_seconds: int = 600,
    **kwargs,
) -> list[dict]:
    """
    Run pipeline with a maximum timeout.

    Args:
        room_url: Daily.co room URL.
        timeout_seconds: Maximum time to run (default 10 minutes).
        **kwargs: Additional args for run_pipeline_for_room.

    Returns:
        Conversation history.
    """
    try:
        return await asyncio.wait_for(
            run_pipeline_for_room(room_url, **kwargs),
            timeout=timeout_seconds,
        )
    except asyncio.TimeoutError:
        logger.warning(f"Pipeline timed out after {timeout_seconds}s")
        return []
