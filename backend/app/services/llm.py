"""
LLM Service

Handles all interactions with Gemini 2.5 Flash-Lite for:
- Generating conversational responses
- Extracting structured data from user input
"""

from typing import Any, Optional

import google.generativeai as genai

from ..config import settings
from ..models.messages import IntakeState


class LLMService:
    """
    Service for LLM interactions using Gemini.

    Responsibilities:
    - Generate contextual responses based on intake state
    - Extract structured data from patient responses
    """

    def __init__(self) -> None:
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash-lite")

    async def generate_response(
        self,
        user_input: str,
        current_state: IntakeState,
        collected_data: dict[str, Any],
        conversation_history: list[dict[str, str]],
    ) -> str:
        """
        Generate the next agent response based on context.

        Args:
            user_input: The patient's latest message
            current_state: Current intake flow state
            collected_data: Data collected so far
            conversation_history: Previous conversation turns

        Returns:
            Agent response text
        """
        system_prompt = self._build_system_prompt(current_state, collected_data)

        # Build messages for the model
        messages = [{"role": "user", "parts": [system_prompt]}]

        for turn in conversation_history[-10:]:  # Keep last 10 turns
            role = "user" if turn["role"] == "user" else "model"
            messages.append({"role": role, "parts": [turn["content"]]})

        messages.append({"role": "user", "parts": [user_input]})

        response = await self.model.generate_content_async(
            messages,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=200,
            ),
        )

        return response.text

    async def extract_data(
        self,
        user_input: str,
        current_state: IntakeState,
    ) -> dict[str, Any]:
        """
        Extract structured data from user input.

        Args:
            user_input: The patient's response
            current_state: Current intake flow state

        Returns:
            Dictionary of extracted field values
        """
        extraction_prompt = self._build_extraction_prompt(current_state, user_input)

        response = await self.model.generate_content_async(
            extraction_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )

        # Parse JSON response
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return {}

    def _build_system_prompt(
        self,
        current_state: IntakeState,
        collected_data: dict[str, Any],
    ) -> str:
        """Build the system prompt for response generation."""
        return f"""You are MedVoice, a friendly and professional AI medical intake assistant.

Current intake section: {current_state.value}
Data collected so far: {collected_data}

Guidelines:
- Be warm, empathetic, and professional
- Ask one question at a time
- Confirm critical information (especially allergies)
- Keep responses concise (1-2 sentences)
- If the patient says something unclear, ask for clarification
- Never provide medical advice

Your task is to continue the intake conversation naturally."""

    def _build_extraction_prompt(
        self,
        current_state: IntakeState,
        user_input: str,
    ) -> str:
        """Build the prompt for data extraction."""
        field_schemas = {
            IntakeState.DEMOGRAPHICS: '{"full_name": "string or null", "date_of_birth": "YYYY-MM-DD or null", "phone": "string or null"}',
            IntakeState.VISIT_REASON: '{"chief_complaint": "string or null", "symptoms": ["list of symptoms"], "duration": "string or null", "severity": "1-10 or null"}',
            IntakeState.MEDICAL_HISTORY: '{"chronic_conditions": ["list"], "surgeries": ["list"], "hospitalizations": ["list"]}',
            IntakeState.MEDICATIONS: '{"medications": [{"name": "string", "dosage": "string or null"}]}',
            IntakeState.ALLERGIES: '{"drug_allergies": ["list"], "food_allergies": ["list"], "reactions": "string or null"}',
        }

        schema = field_schemas.get(current_state, "{}")

        return f"""Extract structured data from the patient's response.

Current section: {current_state.value}
Patient said: "{user_input}"

Return a JSON object with these fields (use null for missing values):
{schema}

Only include fields that were explicitly mentioned. Return valid JSON only."""
