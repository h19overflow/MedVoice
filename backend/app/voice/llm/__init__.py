"""
LLM Module

Provides LLM service and prompt management for voice pipeline.
"""

from backend.app.voice.llm.prompts import (
    MEDICAL_INTAKE_PROMPT,
    get_greeting_message,
    get_system_message,
)
from backend.app.voice.llm.service import create_llm_service

__all__ = [
    "MEDICAL_INTAKE_PROMPT",
    "create_llm_service",
    "get_greeting_message",
    "get_system_message",
]
