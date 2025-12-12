"""
Demo Voice Bot - Deepgram STT/TTS + Gemini LLM

Standalone demo for testing the voice pipeline.
Run: wsl -d Ubuntu -- bash -c "source ~/.local/bin/env && cd /mnt/c/Users/User/Projects/MedVoice && uv run python -m backend.app.demo_bot"
"""

import asyncio
import os
import time

import aiohttp
from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import EndFrame, LLMMessagesFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.services.google.llm import GoogleLLMService
from pipecat.transports.daily.transport import DailyParams, DailyTransport

load_dotenv()


async def create_daily_room() -> str:
    """Create a temporary Daily room."""
    api_key = os.getenv("DAILY_API_KEY")
    if not api_key:
        raise ValueError("DAILY_API_KEY not set")

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.daily.co/v1/rooms",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={"properties": {"exp": int(time.time()) + 3600}},
        ) as response:
            if response.status != 200:
                error = await response.text()
                raise RuntimeError(f"Failed to create room: {error}")
            room = await response.json()
            return room["url"]


async def main() -> None:
    """Run the demo voice bot."""
    # Create room
    print("Creating Daily room...", flush=True)
    room_url = await create_daily_room()
    print(f"Room created: {room_url}", flush=True)

    # Transport - Daily WebRTC
    transport = DailyTransport(
        room_url=room_url,
        token=None,
        bot_name="MedVoice Demo",
        params=DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.3)),
        ),
    )

    # STT - Deepgram Nova-2
    stt = DeepgramSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        model="nova-2-general",
        language="en-US",
    
    )

    # TTS - Deepgram Aura
    tts = DeepgramTTSService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
        voice="aura-asteria-en",
    )

    # LLM - Gemini
    llm = GoogleLLMService(
        api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-2.0-flash",
    )

    # Context with system prompt
    messages = [
        {
            "role": "system",
            "content": """You are a friendly medical intake assistant named MedVoice.
Your job is to collect basic patient information for a doctor's visit.
Keep responses brief (1-2 sentences) since this is a voice conversation.
Be warm, professional, and patient.""",
        }
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    # Pipeline
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
        # Greet the user
        await task.queue_frames(
            [LLMMessagesFrame([{"role": "system", "content": "Greet the patient warmly and ask how you can help them today."}])]
        )

    @transport.event_handler("on_participant_left")
    async def on_left(transport, participant, reason):
        logger.info(f"Participant left: {reason}")
        await task.queue_frame(EndFrame())

    # Run
    runner = PipelineRunner()
    print("=" * 50, flush=True)
    print(f"JOIN THE CALL: {room_url}", flush=True)
    print("=" * 50, flush=True)
    print("Bot is running. Press Ctrl+C to stop.", flush=True)

    await runner.run(task)


if __name__ == "__main__":
    asyncio.run(main())
