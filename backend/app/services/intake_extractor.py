"""
Intake Data Extractor

Extracts structured intake data from conversation history using LLM.
"""

import json
from datetime import datetime

from loguru import logger

from backend.app.config import get_settings
from backend.app.models.intake import (
    Allergies,
    Demographics,
    IntakeData,
    IntakeMetadata,
    MedicalHistory,
    Medication,
    Visit,
)

EXTRACTION_PROMPT = """Extract medical intake information from this conversation.
Return a JSON object with the following structure (use null for missing fields):

{
  "demographics": {
    "full_name": "string or null",
    "date_of_birth": "YYYY-MM-DD or null",
    "phone": "string or null",
    "email": "string or null"
  },
  "visit": {
    "chief_complaint": "main reason for visit or null",
    "symptoms": ["list", "of", "symptoms"],
    "duration": "how long symptoms lasted or null",
    "severity": 1-10 or null
  },
  "medical_history": {
    "chronic_conditions": ["diabetes", "hypertension", etc.],
    "surgeries": ["past surgeries"],
    "hospitalizations": ["past hospitalizations"]
  },
  "medications": [
    {"name": "medication name", "dosage": "dosage or null"}
  ],
  "allergies": {
    "drug_allergies": ["penicillin", etc.],
    "food_allergies": ["peanuts", etc.],
    "reactions": "description of reactions or null"
  }
}

Only include information explicitly mentioned in the conversation.
Return valid JSON only, no markdown or explanations.

CONVERSATION:
"""


def format_conversation(history: list[dict]) -> str:
    """Format conversation history for the prompt."""
    lines = []
    for msg in history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "user":
            lines.append(f"Patient: {content}")
        elif role == "assistant":
            lines.append(f"Assistant: {content}")
    return "\n".join(lines)


async def extract_intake_data(
    conversation_history: list[dict],
    session_id: str = "unknown",
) -> IntakeData:
    """
    Extract structured intake data from conversation.

    Args:
        conversation_history: List of conversation messages.
        session_id: Session identifier for the intake record.

    Returns:
        IntakeData with extracted information.
    """
    if not conversation_history:
        logger.warning("Empty conversation history")
        return _create_empty_intake(session_id)

    try:
        import google.generativeai as genai

        settings = get_settings()
        genai.configure(api_key=settings.google_api_key)

        model = genai.GenerativeModel("gemini-2.0-flash")

        # Build extraction prompt
        conversation_text = format_conversation(conversation_history)
        prompt = EXTRACTION_PROMPT + conversation_text

        # Call Gemini
        response = await model.generate_content_async(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2000,
            ),
        )

        # Parse response
        result_text = response.text.strip()

        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            lines = result_text.split("\n")
            result_text = "\n".join(lines[1:-1])

        data = json.loads(result_text)

        return _parse_extraction_result(data, session_id, len(conversation_history))

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse extraction JSON: {e}")
        return _create_empty_intake(session_id, error=str(e))
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return _create_empty_intake(session_id, error=str(e))


def _parse_extraction_result(
    data: dict,
    session_id: str,
    message_count: int,
) -> IntakeData:
    """Parse LLM extraction result into IntakeData."""
    demographics_data = data.get("demographics", {})
    visit_data = data.get("visit", {})
    history_data = data.get("medical_history", {})
    medications_data = data.get("medications", [])
    allergies_data = data.get("allergies", {})

    # Build demographics
    demographics = Demographics(
        full_name=demographics_data.get("full_name"),
        date_of_birth=demographics_data.get("date_of_birth"),
        phone=demographics_data.get("phone"),
        email=demographics_data.get("email"),
    )

    # Build visit
    visit = Visit(
        chief_complaint=visit_data.get("chief_complaint"),
        symptoms=visit_data.get("symptoms", []),
        duration=visit_data.get("duration"),
        severity=visit_data.get("severity"),
    )

    # Build medical history
    medical_history = MedicalHistory(
        chronic_conditions=history_data.get("chronic_conditions", []),
        surgeries=history_data.get("surgeries", []),
        hospitalizations=history_data.get("hospitalizations", []),
    )

    # Build medications
    medications = []
    for med in medications_data:
        if isinstance(med, dict) and med.get("name"):
            medications.append(Medication(
                name=med["name"],
                dosage=med.get("dosage"),
            ))

    # Build allergies
    allergies = Allergies(
        drug_allergies=allergies_data.get("drug_allergies", []),
        food_allergies=allergies_data.get("food_allergies", []),
        reactions=allergies_data.get("reactions"),
    )

    # Count completed sections
    sections_completed = sum([
        bool(demographics.full_name or demographics.date_of_birth),
        bool(visit.chief_complaint or visit.symptoms),
        bool(medical_history.chronic_conditions or medical_history.surgeries),
        bool(medications),
        bool(allergies.drug_allergies or allergies.food_allergies),
    ])

    return IntakeData(
        session_id=session_id,
        timestamp=datetime.utcnow(),
        status="complete",
        demographics=demographics,
        visit=visit,
        medical_history=medical_history,
        medications=medications,
        allergies=allergies,
        metadata=IntakeMetadata(
            sections_completed=sections_completed,
        ),
    )


def _create_empty_intake(session_id: str, error: str | None = None) -> IntakeData:
    """Create an empty intake record."""
    return IntakeData(
        session_id=session_id,
        timestamp=datetime.utcnow(),
        status="incomplete" if error else "in_progress",
        demographics=Demographics(),
        visit=Visit(),
        medical_history=MedicalHistory(),
        medications=[],
        allergies=Allergies(),
        metadata=IntakeMetadata(),
    )
