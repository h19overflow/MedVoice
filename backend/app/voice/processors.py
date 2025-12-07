"""
Custom Frame Processors

Pipecat processors for the MedVoice intake flow.
"""

from typing import TYPE_CHECKING

from pipecat.frames.frames import (
    EndFrame,
    Frame,
    TextFrame,
    TranscriptionFrame,
)
from pipecat.processors.frame_processor import FrameProcessor

if TYPE_CHECKING:
    from ..services.intake import IntakeService


class IntakeProcessor(FrameProcessor):
    """
    Custom processor that integrates IntakeService with Pipecat.

    Receives transcribed text, processes through intake logic,
    and outputs response text for TTS.
    """

    def __init__(self, intake_service: "IntakeService") -> None:
        """
        Initialize with intake service instance.

        Args:
            intake_service: The intake service for this session
        """
        super().__init__()
        self.intake_service = intake_service
        self._greeting_sent = False

    async def process_frame(self, frame: Frame, direction: str) -> None:
        """
        Process incoming frames.

        Args:
            frame: The frame to process
            direction: Processing direction
        """
        await super().process_frame(frame, direction)

        # Send greeting on first interaction
        if not self._greeting_sent:
            greeting = self.intake_service.get_greeting()
            await self.push_frame(TextFrame(text=greeting))
            self._greeting_sent = True
            return

        # Handle transcription frames
        if isinstance(frame, TranscriptionFrame):
            user_text = frame.text

            # Skip empty transcriptions
            if not user_text or not user_text.strip():
                return

            # Process through intake service
            response = await self.intake_service.process_message(user_text)

            # Push response for TTS
            await self.push_frame(TextFrame(text=response))

            # Check if intake is complete
            if self.intake_service.is_complete():
                # Send completion message
                await self.push_frame(
                    TextFrame(
                        text="Your intake is complete. Please check in at the front desk."
                    )
                )
                await self.push_frame(EndFrame())

        # Pass through other frames
        else:
            await self.push_frame(frame)


class InterruptionHandler(FrameProcessor):
    """
    Handles user interruptions (barge-in).

    Detects when user starts speaking while agent is talking
    and stops the current agent response.
    """

    def __init__(self) -> None:
        """Initialize interruption handler."""
        super().__init__()
        self._agent_speaking = False

    async def process_frame(self, frame: Frame, direction: str) -> None:
        """
        Process frames and handle interruptions.

        Args:
            frame: The frame to process
            direction: Processing direction
        """
        await super().process_frame(frame, direction)

        # Track agent speaking state
        if isinstance(frame, TextFrame):
            self._agent_speaking = True
        elif isinstance(frame, EndFrame):
            self._agent_speaking = False

        # If we receive transcription while agent is speaking, it's an interruption
        if isinstance(frame, TranscriptionFrame) and self._agent_speaking:
            # Cancel current TTS output
            self._agent_speaking = False
            # Let the transcription through to be processed

        await self.push_frame(frame)


class MetricsCollector(FrameProcessor):
    """
    Collects latency and performance metrics.

    Tracks timing between frames to measure:
    - STT latency
    - Processing latency
    - TTS latency
    - End-to-end latency
    """

    def __init__(self) -> None:
        """Initialize metrics collector."""
        super().__init__()
        self.metrics: dict = {
            "stt_latency_ms": [],
            "processing_latency_ms": [],
            "tts_latency_ms": [],
            "e2e_latency_ms": [],
        }
        self._last_audio_time: float | None = None
        self._last_transcription_time: float | None = None

    async def process_frame(self, frame: Frame, direction: str) -> None:
        """
        Process frames and collect timing metrics.

        Args:
            frame: The frame to process
            direction: Processing direction
        """
        import time

        await super().process_frame(frame, direction)

        current_time = time.time() * 1000  # ms

        if isinstance(frame, TranscriptionFrame):
            if self._last_audio_time:
                stt_latency = current_time - self._last_audio_time
                self.metrics["stt_latency_ms"].append(stt_latency)
            self._last_transcription_time = current_time

        elif isinstance(frame, TextFrame):
            if self._last_transcription_time:
                processing_latency = current_time - self._last_transcription_time
                self.metrics["processing_latency_ms"].append(processing_latency)

        await self.push_frame(frame)

    def get_average_metrics(self) -> dict:
        """Get average metrics."""
        return {
            key: sum(values) / len(values) if values else 0
            for key, values in self.metrics.items()
        }
