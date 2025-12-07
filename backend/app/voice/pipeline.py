"""
Voice Pipeline

Pipecat pipeline configuration for real-time voice processing.
"""

from typing import TYPE_CHECKING

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_response import LLMResponseAggregator
from pipecat.processors.aggregators.sentence import SentenceAggregator
from pipecat.services.deepgram import DeepgramSTTService, DeepgramTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport
from pipecat.vad.silero import SileroVADAnalyzer

from ..config import settings
from .processors import IntakeProcessor

if TYPE_CHECKING:
    from ..services.intake import IntakeService


async def create_pipeline(
    room_url: str,
    token: str,
    intake_service: "IntakeService",
) -> PipelineTask:
    """
    Create the voice processing pipeline.

    Pipeline flow:
    1. Daily.co transport receives audio
    2. Silero VAD detects speech
    3. Deepgram STT transcribes audio
    4. IntakeProcessor handles intake logic
    5. Deepgram TTS synthesizes response
    6. Daily.co transport sends audio

    Args:
        room_url: Daily.co room URL
        token: Daily.co authentication token
        intake_service: The intake service instance for this session

    Returns:
        Configured PipelineTask ready to run
    """
    # Transport - Daily.co WebRTC
    transport = DailyTransport(
        room_url=room_url,
        token=token,
        bot_name="MedVoice",
        params=DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    # Speech-to-Text - Deepgram Nova-2
    stt = DeepgramSTTService(
        api_key=settings.deepgram_api_key,
        model="nova-2",
        language="en",
    )

    # Text-to-Speech - Deepgram Aura
    tts = DeepgramTTSService(
        api_key=settings.deepgram_api_key,
        voice="aura-asteria-en",
    )

    # Custom intake processor
    intake_processor = IntakeProcessor(intake_service)

    # Aggregators for smooth processing
    sentence_aggregator = SentenceAggregator()
    llm_response_aggregator = LLMResponseAggregator()

    # Build the pipeline
    pipeline = Pipeline([
        transport.input(),           # Audio in from Daily.co
        stt,                          # Transcribe speech
        sentence_aggregator,          # Wait for complete sentences
        intake_processor,             # Process through intake logic
        llm_response_aggregator,      # Aggregate LLM response
        tts,                          # Convert to speech
        transport.output(),           # Audio out to Daily.co
    ])

    # Create task
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,
            enable_metrics=True,
        ),
    )

    return task


async def run_pipeline(
    room_url: str,
    token: str,
    intake_service: "IntakeService",
) -> None:
    """
    Run the voice pipeline until completion.

    Args:
        room_url: Daily.co room URL
        token: Daily.co authentication token
        intake_service: The intake service instance
    """
    task = await create_pipeline(room_url, token, intake_service)

    runner = PipelineRunner()
    await runner.run(task)
