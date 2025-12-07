"""
Intake Service

Core business logic for the patient intake flow.
Implements the state machine and coordinates data extraction.
"""

import uuid
from datetime import datetime
from typing import Any

from ..models.intake import (
    Allergies,
    Demographics,
    IntakeData,
    MedicalHistory,
    Medication,
    Visit,
)
from ..models.messages import (
    ChatMessage,
    ConversationTurn,
    IntakeState,
    SessionState,
    SessionStatus,
)
from .llm import LLMService


class IntakeService:
    """
    Manages a single patient intake session.

    Responsibilities:
    - Track conversation state
    - Process patient messages
    - Coordinate with LLM for responses and extraction
    - Maintain collected data
    """

    def __init__(self, session_id: str | None = None) -> None:
        """Initialize a new intake session."""
        self.session_id = session_id or str(uuid.uuid4())
        self.state = IntakeState.GREETING
        self.data = IntakeData(session_id=self.session_id)
        self.turns: list[ConversationTurn] = []
        self.llm = LLMService()
        self.start_time = datetime.utcnow()

    async def process_message(self, user_input: str) -> str:
        """
        Process a patient message and generate response.

        This is the main entry point used by both voice and chat modes.

        Args:
            user_input: The patient's message text

        Returns:
            Agent response text
        """
        # Record patient turn
        self._add_turn("patient", user_input)

        # Extract data from input based on current state
        extracted = await self._extract_data(user_input)
        self._update_data(extracted)

        # Determine if we should transition to next state
        self._maybe_transition_state()

        # Generate response
        response = await self._generate_response(user_input)

        # Record agent turn
        self._add_turn("agent", response)

        return response

    def get_greeting(self) -> str:
        """Get the initial greeting message."""
        greeting = (
            "Hi! I'm MedVoice, your virtual intake assistant. "
            "I'll ask you a few questions to prepare for your visit today. "
            "This should take about 3 to 4 minutes. Let's start - what's your full name?"
        )
        self._add_turn("agent", greeting)
        self.state = IntakeState.DEMOGRAPHICS
        return greeting

    def get_session_state(self) -> SessionState:
        """Get the current session state."""
        return SessionState(
            session_id=self.session_id,
            status=self._get_status(),
            current_state=self.state,
            turns=self.turns,
            created_at=self.start_time,
            updated_at=datetime.utcnow(),
        )

    def get_intake_data(self) -> IntakeData:
        """Get the collected intake data."""
        self.data.metadata.duration_seconds = int(
            (datetime.utcnow() - self.start_time).total_seconds()
        )
        return self.data

    def is_complete(self) -> bool:
        """Check if the intake is complete."""
        return self.state == IntakeState.COMPLETE

    def _add_turn(self, speaker: str, text: str) -> None:
        """Add a conversation turn."""
        turn = ConversationTurn(
            turn_id=len(self.turns) + 1,
            speaker=speaker,
            text=text,
            state=self.state,
        )
        self.turns.append(turn)

    async def _extract_data(self, user_input: str) -> dict[str, Any]:
        """Extract structured data from user input."""
        if self.state in (IntakeState.GREETING, IntakeState.CONFIRMATION, IntakeState.COMPLETE):
            return {}

        return await self.llm.extract_data(user_input, self.state)

    def _update_data(self, extracted: dict[str, Any]) -> None:
        """Update intake data with extracted values."""
        if not extracted:
            return

        if self.state == IntakeState.DEMOGRAPHICS:
            if "full_name" in extracted and extracted["full_name"]:
                self.data.demographics.full_name = extracted["full_name"]
            if "date_of_birth" in extracted and extracted["date_of_birth"]:
                self.data.demographics.date_of_birth = extracted["date_of_birth"]
            if "phone" in extracted and extracted["phone"]:
                self.data.demographics.phone = extracted["phone"]

        elif self.state == IntakeState.VISIT_REASON:
            if "chief_complaint" in extracted and extracted["chief_complaint"]:
                self.data.visit.chief_complaint = extracted["chief_complaint"]
            if "symptoms" in extracted and extracted["symptoms"]:
                self.data.visit.symptoms.extend(extracted["symptoms"])
            if "duration" in extracted and extracted["duration"]:
                self.data.visit.duration = extracted["duration"]
            if "severity" in extracted and extracted["severity"]:
                self.data.visit.severity = extracted["severity"]

        elif self.state == IntakeState.MEDICAL_HISTORY:
            if "chronic_conditions" in extracted:
                self.data.medical_history.chronic_conditions.extend(
                    extracted["chronic_conditions"]
                )
            if "surgeries" in extracted:
                self.data.medical_history.surgeries.extend(extracted["surgeries"])
            if "hospitalizations" in extracted:
                self.data.medical_history.hospitalizations.extend(
                    extracted["hospitalizations"]
                )

        elif self.state == IntakeState.MEDICATIONS:
            if "medications" in extracted:
                for med in extracted["medications"]:
                    self.data.medications.append(
                        Medication(name=med["name"], dosage=med.get("dosage"))
                    )

        elif self.state == IntakeState.ALLERGIES:
            if "drug_allergies" in extracted:
                self.data.allergies.drug_allergies.extend(extracted["drug_allergies"])
            if "food_allergies" in extracted:
                self.data.allergies.food_allergies.extend(extracted["food_allergies"])
            if "reactions" in extracted and extracted["reactions"]:
                self.data.allergies.reactions = extracted["reactions"]

    def _maybe_transition_state(self) -> None:
        """Check if we should transition to the next state."""
        # Simple transition logic - can be enhanced with more sophisticated checks
        transitions = {
            IntakeState.DEMOGRAPHICS: self._demographics_complete,
            IntakeState.VISIT_REASON: self._visit_complete,
            IntakeState.MEDICAL_HISTORY: self._history_complete,
            IntakeState.MEDICATIONS: self._medications_complete,
            IntakeState.ALLERGIES: self._allergies_complete,
            IntakeState.CONFIRMATION: self._confirmation_complete,
        }

        check_fn = transitions.get(self.state)
        if check_fn and check_fn():
            self._advance_state()

    def _advance_state(self) -> None:
        """Move to the next state."""
        state_order = [
            IntakeState.GREETING,
            IntakeState.DEMOGRAPHICS,
            IntakeState.VISIT_REASON,
            IntakeState.MEDICAL_HISTORY,
            IntakeState.MEDICATIONS,
            IntakeState.ALLERGIES,
            IntakeState.CONFIRMATION,
            IntakeState.COMPLETE,
        ]
        current_idx = state_order.index(self.state)
        if current_idx < len(state_order) - 1:
            self.state = state_order[current_idx + 1]
            self.data.metadata.sections_completed += 1

    def _demographics_complete(self) -> bool:
        """Check if demographics section is complete."""
        d = self.data.demographics
        return bool(d.full_name and d.date_of_birth and d.phone)

    def _visit_complete(self) -> bool:
        """Check if visit reason section is complete."""
        v = self.data.visit
        return bool(v.chief_complaint)

    def _history_complete(self) -> bool:
        """Check if medical history section is complete."""
        # History can be empty, always allow progression after asking
        return len(self.turns) >= 2  # At least one Q&A

    def _medications_complete(self) -> bool:
        """Check if medications section is complete."""
        # Medications can be empty
        return len(self.turns) >= 2

    def _allergies_complete(self) -> bool:
        """Check if allergies section is complete."""
        # Must explicitly confirm allergies
        return len(self.turns) >= 2

    def _confirmation_complete(self) -> bool:
        """Check if confirmation is done."""
        # Look for affirmative in last response
        if self.turns:
            last = self.turns[-1].text.lower()
            return any(word in last for word in ["yes", "correct", "right", "confirm"])
        return False

    async def _generate_response(self, user_input: str) -> str:
        """Generate the agent's response."""
        # Build conversation history for context
        history = [
            {"role": "user" if t.speaker == "patient" else "assistant", "content": t.text}
            for t in self.turns[-10:]
        ]

        collected = self.data.model_dump(exclude={"session_id", "timestamp", "metadata"})

        return await self.llm.generate_response(
            user_input=user_input,
            current_state=self.state,
            collected_data=collected,
            conversation_history=history,
        )

    def _get_status(self) -> SessionStatus:
        """Get the session status."""
        if self.state == IntakeState.COMPLETE:
            return SessionStatus.COMPLETE
        return SessionStatus.ACTIVE


# In-memory session store
_sessions: dict[str, IntakeService] = {}


def get_session(session_id: str) -> IntakeService | None:
    """Get an existing session by ID."""
    return _sessions.get(session_id)


def create_session() -> IntakeService:
    """Create a new intake session."""
    service = IntakeService()
    _sessions[service.session_id] = service
    return service


def delete_session(session_id: str) -> bool:
    """Delete a session."""
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False
