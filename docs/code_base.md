# MedVoice Codebase Architecture

**Purpose:** Technical reference for the MedVoice AI-powered patient intake system
**Based on:** PRD v1.0 (December 2025)

---

## Project Structure

```
medvoice/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app factory, CORS, route mounting
│       ├── config.py            # Pydantic Settings (loads .env)
│       │
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── sessions.py      # POST /api/sessions - create intake
│       │   ├── chat.py          # POST /api/sessions/{id}/chat
│       │   └── voice.py         # WS /api/sessions/{id}/voice (Pipecat)
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── llm.py           # Gemini 2.5 Flash-Lite integration
│       │   ├── intake.py        # Intake state machine + data extraction
│       │   └── transcription.py # STT/TTS wrappers (if needed outside voice)
│       │
│       ├── voice/
│       │   ├── __init__.py
│       │   ├── pipeline.py      # Pipecat pipeline definition
│       │   └── processors.py    # Custom frame processors
│       │
│       └── models/
│           ├── __init__.py
│           ├── intake.py        # IntakeData, PatientInfo schemas
│           └── messages.py      # ChatMessage, SessionState schemas
│
├── frontend/
│   └── src/
│       ├── App.tsx              # Router setup
│       │
│       ├── pages/
│       │   ├── Landing.tsx      # Hero, value prop, CTAs
│       │   ├── VoiceIntake.tsx  # Voice interface (primary)
│       │   ├── ChatIntake.tsx   # Chat interface (future)
│       │   └── Results.tsx      # Display extracted data
│       │
│       ├── components/
│       │   ├── ui/              # shadcn components
│       │   ├── StatusIndicator.tsx
│       │   ├── Transcript.tsx
│       │   ├── ChatMessages.tsx
│       │   └── IntakeProgress.tsx
│       │
│       ├── hooks/
│       │   ├── useVoiceSession.ts   # Daily.co + Pipecat client
│       │   ├── useChatSession.ts    # REST API chat
│       │   └── useIntakeState.ts    # Shared intake state
│       │
│       └── lib/
│           ├── api.ts           # API client (fetch wrappers)
│           └── utils.ts         # Helpers
│
└── docs/
    ├── plan.md                  # Product Requirements Document
    └── code_base.md             # This file
```

---

## Tech Stack

| Component        | Technology           | Rationale                          |
|------------------|----------------------|------------------------------------|
| Voice Framework  | Pipecat              | Best open-source voice agent framework |
| WebRTC Transport | Daily.co             | Built by Pipecat team, free tier   |
| STT              | Deepgram Nova-2      | Fast, accurate, $200 free credit   |
| TTS              | Deepgram Aura        | Same provider, low latency         |
| LLM              | Gemini 2.5 Flash-Lite| Free tier, fast, good quality      |
| VAD              | Silero               | Best open-source VAD               |
| Backend          | FastAPI              | Async Python, fast                 |
| Frontend         | React + Vite         | Fast dev, simple                   |
| Styling          | Tailwind CSS         | Rapid UI development               |

---

## Core Design Patterns

### 1. Shared Intake Service

Both voice and chat modes use the same intake logic:

```python
# services/intake.py
class IntakeService:
    def __init__(self):
        self.state = "GREETING"
        self.data = IntakeData()

    async def process_message(self, user_input: str) -> str:
        """Same logic for voice and chat"""
        # 1. Extract data from input
        # 2. Update state machine
        # 3. Generate next prompt via LLM
        return agent_response
```

- Voice pipeline calls `intake_service.process_message(transcribed_text)`
- Chat endpoint calls `intake_service.process_message(chat_message)`

### 2. Session Management (In-Memory)

```python
# Simple session store (no database for MVP)
sessions: dict[str, IntakeService] = {}

def get_session(session_id: str) -> IntakeService:
    if session_id not in sessions:
        sessions[session_id] = IntakeService()
    return sessions[session_id]
```

### 3. Voice Pipeline (Pipecat)

```python
# voice/pipeline.py
pipeline = Pipeline([
    transport.input(),      # Audio in from Daily.co
    stt,                    # Deepgram transcription
    intake_processor,       # Custom processor (calls IntakeService)
    tts,                    # Deepgram speech synthesis
    transport.output(),     # Audio out to Daily.co
])
```

---

## Intake State Machine

```
GREETING → DEMOGRAPHICS → VISIT_REASON → MEDICAL_HISTORY → MEDICATIONS → ALLERGIES → CONFIRMATION → COMPLETE
```

| State           | Fields Collected                                    |
|-----------------|-----------------------------------------------------|
| GREETING        | —                                                   |
| DEMOGRAPHICS    | full_name, date_of_birth, phone                     |
| VISIT_REASON    | chief_complaint, symptoms, duration, severity       |
| MEDICAL_HISTORY | chronic_conditions, surgeries, hospitalizations    |
| MEDICATIONS     | medications[] (name, dosage)                        |
| ALLERGIES       | drug_allergies, food_allergies, reactions (⚠️ critical) |
| CONFIRMATION    | Read back all data, get user confirmation           |
| COMPLETE        | Generate summary, display results                   |

---

## API Endpoints

| Method | Endpoint                      | Purpose                        |
|--------|-------------------------------|--------------------------------|
| POST   | `/api/sessions`               | Create new intake session      |
| GET    | `/api/sessions/{id}`          | Get session state + data       |
| POST   | `/api/sessions/{id}/chat`     | Send chat message              |
| GET    | `/api/sessions/{id}/results`  | Get final extracted data       |
| WS     | `/api/sessions/{id}/voice`    | WebSocket for voice (Pipecat)  |

---

## Data Models

### IntakeData (Output)

```json
{
  "session_id": "uuid",
  "timestamp": "2025-12-07T10:30:00Z",
  "status": "complete",
  "demographics": {
    "full_name": "John Smith",
    "date_of_birth": "1985-03-15",
    "phone": "555-123-4567"
  },
  "visit": {
    "chief_complaint": "Persistent headache",
    "symptoms": ["headache", "nausea", "light sensitivity"],
    "duration": "3 days",
    "severity": 7
  },
  "medical_history": {
    "chronic_conditions": ["hypertension"],
    "surgeries": ["appendectomy 2010"],
    "hospitalizations": []
  },
  "medications": [
    { "name": "lisinopril", "dosage": "10mg daily" }
  ],
  "allergies": {
    "drug_allergies": ["penicillin"],
    "food_allergies": [],
    "reactions": "rash and swelling"
  },
  "metadata": {
    "duration_seconds": 195,
    "sections_completed": 6,
    "corrections_made": 1
  }
}
```

---

## Data Flow

### Voice Mode
```
User speaks → Daily.co WebRTC → Pipecat Server → Deepgram STT → IntakeService → Gemini LLM → Deepgram TTS → Daily.co → User hears
```

### Chat Mode
```
User types → POST /chat → IntakeService → Gemini LLM → Response → Display
```

---

## Performance Targets

| Metric              | Target    |
|---------------------|-----------|
| End-to-end latency  | < 800ms   |
| STT latency         | < 300ms   |
| LLM latency (TTFB)  | < 400ms   |
| TTS latency (TTFB)  | < 200ms   |
| Concurrent users    | 1 (demo)  |

---

## MVP Exclusions

| Not Needed          | Reason              |
|---------------------|---------------------|
| Database            | In-memory dict      |
| User auth           | Demo only           |
| Redis               | No scaling needed   |
| Celery              | No background jobs  |
| Microservices       | Single app          |
| HIPAA compliance    | Demo only           |

---

## Environment Variables

```env
# Required
DEEPGRAM_API_KEY=       # STT/TTS
GEMINI_API_KEY=         # LLM
DAILY_API_KEY=          # WebRTC transport

# Optional
DEBUG=false
LOG_LEVEL=INFO
```

---

*End of Document*
