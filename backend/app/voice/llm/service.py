"""
LLM Service Factory

Creates Google Gemini LLM service for voice pipeline.
"""

from pipecat.services.google.llm import GoogleLLMService

from backend.app.config import get_settings


def create_llm_service(model: str = "gemini-2.0-flash") -> GoogleLLMService:
    """
    Create a Google Gemini LLM service.

    Args:
        model: Gemini model name to use.

    Returns:
        Configured GoogleLLMService instance.
    """
    settings = get_settings()
    return GoogleLLMService(
        api_key=settings.google_api_key,
        model=model,
    )
