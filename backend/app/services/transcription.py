"""
Transcription Service

Wrapper for STT/TTS operations outside of the Pipecat voice pipeline.
Used for testing and potential future chat-to-voice features.
"""

from typing import Optional

from deepgram import DeepgramClient, PrerecordedOptions

from ..config import settings


class TranscriptionService:
    """
    Service for speech-to-text and text-to-speech operations.

    Note: In voice mode, Pipecat handles STT/TTS directly.
    This service is for auxiliary transcription needs.
    """

    def __init__(self) -> None:
        """Initialize Deepgram client."""
        self.client = DeepgramClient(settings.deepgram_api_key)

    async def transcribe_audio(
        self,
        audio_data: bytes,
        mimetype: str = "audio/wav",
    ) -> Optional[str]:
        """
        Transcribe audio data to text.

        Args:
            audio_data: Raw audio bytes
            mimetype: Audio MIME type

        Returns:
            Transcribed text or None if failed
        """
        options = PrerecordedOptions(
            model="nova-2",
            language="en",
            smart_format=True,
        )

        response = await self.client.listen.asyncrest.v("1").transcribe_file(
            {"buffer": audio_data, "mimetype": mimetype},
            options,
        )

        # Extract transcript from response
        try:
            return response.results.channels[0].alternatives[0].transcript
        except (AttributeError, IndexError):
            return None

    async def synthesize_speech(
        self,
        text: str,
        voice: str = "aura-asteria-en",
    ) -> Optional[bytes]:
        """
        Convert text to speech audio.

        Args:
            text: Text to synthesize
            voice: Deepgram voice model name

        Returns:
            Audio bytes or None if failed
        """
        # Deepgram TTS endpoint
        options = {
            "model": voice,
        }

        response = await self.client.speak.asyncrest.v("1").stream_memory(
            {"text": text},
            options,
        )

        return response.stream_memory.getvalue()
