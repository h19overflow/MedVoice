"""
Intake Data Models

Pydantic schemas for structured patient intake data.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Demographics(BaseModel):
    """Patient demographic information."""

    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO format: YYYY-MM-DD
    phone: Optional[str] = None
    email: Optional[str] = None


class Visit(BaseModel):
    """Visit reason and symptom information."""

    chief_complaint: Optional[str] = None
    symptoms: list[str] = Field(default_factory=list)
    duration: Optional[str] = None
    severity: Optional[int] = Field(default=None, ge=1, le=10)


class MedicalHistory(BaseModel):
    """Patient medical history."""

    chronic_conditions: list[str] = Field(default_factory=list)
    surgeries: list[str] = Field(default_factory=list)
    hospitalizations: list[str] = Field(default_factory=list)


class Medication(BaseModel):
    """Single medication entry."""

    name: str
    dosage: Optional[str] = None


class Allergies(BaseModel):
    """Patient allergy information (critical section)."""

    drug_allergies: list[str] = Field(default_factory=list)
    food_allergies: list[str] = Field(default_factory=list)
    reactions: Optional[str] = None


class IntakeMetadata(BaseModel):
    """Metadata about the intake session."""

    duration_seconds: int = 0
    sections_completed: int = 0
    corrections_made: int = 0


class IntakeData(BaseModel):
    """Complete intake data structure."""

    session_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: str = "in_progress"  # in_progress, complete, abandoned

    demographics: Demographics = Field(default_factory=Demographics)
    visit: Visit = Field(default_factory=Visit)
    medical_history: MedicalHistory = Field(default_factory=MedicalHistory)
    medications: list[Medication] = Field(default_factory=list)
    allergies: Allergies = Field(default_factory=Allergies)

    metadata: IntakeMetadata = Field(default_factory=IntakeMetadata)
