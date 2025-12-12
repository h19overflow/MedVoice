"""
System Prompts for Voice Pipeline

Contains prompt templates for medical intake conversations.
"""

MEDICAL_INTAKE_PROMPT = """You are a friendly medical intake assistant named MedVoice.
Your job is to collect basic patient information for a doctor's visit.
Keep responses brief (1-2 sentences) since this is a voice conversation.
Be warm, professional, and patient."""


def get_system_message(prompt: str = MEDICAL_INTAKE_PROMPT) -> dict[str, str]:
    """Create a system message dict for LLM context."""
    return {"role": "system", "content": prompt}


def get_greeting_message() -> dict[str, str]:
    """Create a greeting trigger message."""
    return {
        "role": "system",
        "content": "Greet the patient warmly and ask how you can help them today.",
    }
