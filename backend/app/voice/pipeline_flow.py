"""
Voice Pipeline Flow

Main orchestrator for the voice bot pipeline.
Run: python -m backend.app.voice.pipeline_flow
"""

import asyncio

from loguru import logger
from pipecat.frames.frames import EndFrame, LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.daily.transport import DailyTransport

from backend.app.voice.context import create_context
from backend.app.voice.llm import (
    create_llm_service,
    get_greeting_message,
    get_system_message,
)
from backend.app.voice.room import create_daily_room
from backend.app.voice.stt import create_stt_service
from backend.app.voice.transport import create_transport
from backend.app.voice.tts import create_tts_service


def create_pipeline(
    transport: DailyTransport,
    stt,
    llm: GoogleLLMService,
    tts,
    context_aggregator,
) -> Pipeline:
    """
    Create the voice processing pipeline.

    Args:
        transport: Daily WebRTC transport.
        stt: Speech-to-text service.
        llm: Language model service.
        tts: Text-to-speech service.
        context_aggregator: LLM context aggregator.

    Returns:
        Configured Pipeline instance.
    """
    return Pipeline(
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


def create_pipeline_task(pipeline: Pipeline) -> PipelineTask:
    """
    Create a pipeline task with standard params.

    Args:
        pipeline: The pipeline to run.

    Returns:
        Configured PipelineTask instance.
    """
    return PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
    )


def setup_event_handlers(transport: DailyTransport, task: PipelineTask) -> None:
    """
    Set up event handlers for participant events.

    Args:
        transport: Daily transport to attach handlers to.
        task: Pipeline task to control.
    """

    @transport.event_handler("on_first_participant_joined")
    async def on_joined(transport, participant):
        logger.info(f"Participant joined: {participant['id']}")
        await task.queue_frames([LLMMessagesFrame([get_greeting_message()])])

    @transport.event_handler("on_participant_left")
    async def on_left(transport, participant, reason):
        logger.info(f"Participant left: {reason}")
        await task.queue_frame(EndFrame())


async def run_voice_bot() -> None:
    """Run the voice bot pipeline."""
    print("Creating Daily room...", flush=True)
    room_url = await create_daily_room()
    print(f"Room created: {room_url}", flush=True)

    # Create services
    transport = create_transport(room_url)
    stt = create_stt_service()
    tts = create_tts_service()
    llm = create_llm_service()

    # Create context with system prompt
    context = create_context([get_system_message()])
    context_aggregator = llm.create_context_aggregator(context)

    # Build pipeline
    pipeline = create_pipeline(transport, stt, llm, tts, context_aggregator)
    task = create_pipeline_task(pipeline)

    # Set up events
    setup_event_handlers(transport, task)

    # Run
    runner = PipelineRunner()
    print("=" * 50, flush=True)
    print(f"JOIN THE CALL: {room_url}", flush=True)
    print("=" * 50, flush=True)
    print("Bot is running. Press Ctrl+C to stop.", flush=True)

    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(run_voice_bot())
