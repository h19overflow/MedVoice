# MedVoice Minimal Implementation Plan

**Goal**: Portfolio-ready voice agent demo for medical intake
**Estimated effort**: ~3 days of focused work
**Principle**: Ship the voice demo, mock everything else

---

## Detailed Phase Documentation

Each phase has a dedicated README with implementation details:

| Phase | Directory | Focus |
|-------|-----------|-------|
| **Phase 1** | [phases/phase1-backend-api/](./phases/phase1-backend-api/) | FastAPI routes, session store |
| **Phase 2** | [phases/phase2-voice-pipeline/](./phases/phase2-voice-pipeline/) | Pipecat integration, intake extraction |
| **Phase 3** | [phases/phase3-frontend/](./phases/phase3-frontend/) | React/Daily.co integration |
| **Phase 4** | [phases/phase4-polish/](./phases/phase4-polish/) | Error handling, demo prep |

---

## Architecture Overview

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│   React Frontend │◄──────────────────►│  FastAPI Backend │
│   (VoiceIntake)  │                    │                  │
└────────┬────────┘                    └────────┬─────────┘
         │                                      │
         │  Daily.co WebRTC                     │ Pipecat Pipeline
         │                                      │
         ▼                                      ▼
┌─────────────────┐                    ┌─────────────────┐
│   Daily.co Room  │◄──────────────────►│  Voice Pipeline  │
│   (Audio/Video)  │                    │  STT→LLM→TTS    │
└─────────────────┘                    └─────────────────┘
```

---

## Phase 1: Backend API Foundation

**Directory**: `backend/app/routes/` and `backend/app/services/`
**Goal**: Create minimal API to manage sessions and serve voice pipeline

### Tasks

#### 1.1 Session Store (In-Memory)
- File: `backend/app/services/session_store.py`
- Simple dict-based storage for demo
- No database needed
- Store: session_id → SessionState mapping

#### 1.2 Session Routes
- File: `backend/app/routes/sessions.py`
- `POST /api/sessions/` - Create new session + Daily room
- `GET /api/sessions/{session_id}/` - Get session state
- `DELETE /api/sessions/{session_id}/` - End session (optional)

#### 1.3 FastAPI App Setup
- File: `backend/app/main.py`
- Mount routes
- Configure CORS for frontend
- Add lifespan for cleanup

#### 1.4 Voice Bot Runner
- File: `backend/app/services/bot_runner.py`
- Wrapper to start voice pipeline for a session
- Manages Pipecat task lifecycle
- Captures intake data on completion

### Deliverable
```bash
# Test: Create session
curl -X POST http://localhost:8000/api/sessions/
# Returns: {"session_id": "abc123", "room_url": "https://medvoice.daily.co/abc123"}
```

---

## Phase 2: Voice Pipeline Integration

**Directory**: `backend/app/voice/`
**Goal**: Connect existing voice components into runnable pipeline

### Tasks

#### 2.1 Pipeline Runner
- File: `backend/app/voice/runner.py`
- Orchestrate: Transport → VAD → STT → LLM → TTS
- Use existing factory functions
- Handle pipeline lifecycle (start/stop/error)

#### 2.2 Intake Extraction
- File: `backend/app/services/intake_extractor.py`
- Parse LLM conversation for structured intake data
- Map to existing `IntakeData` Pydantic model
- Called when session completes

#### 2.3 Event Handlers
- File: `backend/app/voice/handlers.py`
- On conversation end → extract intake → update session
- On error → mark session failed
- On user disconnect → cleanup

#### 2.4 System Prompt Refinement
- File: `backend/app/voice/llm/prompts.py` (existing)
- Ensure prompt guides toward structured data collection
- Add completion detection logic

### Deliverable
```bash
# Bot joins Daily room and responds to voice
# Session state updates with intake data on completion
```

---

## Phase 3: Frontend Integration

**Directory**: `medvoice-assistant/src/`
**Goal**: Connect React UI to real backend

### Tasks

#### 3.1 API Client
- File: `medvoice-assistant/src/lib/api.ts`
- `createSession()` - POST /api/sessions/
- `getSession(id)` - GET /api/sessions/{id}/
- Type-safe with Zod validation

#### 3.2 Daily.co Integration
- File: `medvoice-assistant/src/lib/daily.ts`
- Initialize Daily call frame
- Join room with URL from backend
- Handle audio permissions

#### 3.3 VoiceIntake Page Update
- File: `medvoice-assistant/src/pages/VoiceIntake.tsx`
- Replace mock with real flow:
  1. Call `createSession()` on mount
  2. Join Daily room
  3. Show live status (listening/speaking)
  4. On complete → navigate to Results

#### 3.4 Results Page Update
- File: `medvoice-assistant/src/pages/Results.tsx`
- Fetch real session data
- Display extracted intake JSON
- Show conversation transcript (if available)

### Deliverable
```
User clicks "Start" → Daily room joins → Voice conversation → Results displayed
```

---

## Phase 4: Polish & Demo Ready

**Directory**: Various
**Goal**: Make it demo-worthy

### Tasks

#### 4.1 Error Handling
- Graceful fallbacks for:
  - Daily.co connection failures
  - Microphone permission denied
  - API timeouts
- User-friendly error messages

#### 4.2 Loading States
- Skeleton loaders during session creation
- "Connecting..." indicator for Daily
- Processing indicator during STT/LLM

#### 4.3 Demo Script
- File: `docs/demo_script.md`
- Step-by-step demo walkthrough
- Sample phrases that work well
- Known limitations

#### 4.4 Environment Setup
- File: `docs/setup.md`
- Required API keys (Deepgram, Google, Daily)
- How to run locally
- Troubleshooting common issues

### Deliverable
```
Polished demo ready for portfolio/interviews
```

---

## File Structure After Implementation

```
backend/app/
├── main.py                      # FastAPI app entry [NEW]
├── config.py                    # Settings [EXISTS]
├── models/
│   ├── intake.py               # Intake schema [EXISTS]
│   └── messages.py             # Session state [EXISTS]
├── routes/
│   ├── __init__.py             # Router aggregation [NEW]
│   └── sessions.py             # Session endpoints [NEW]
├── services/
│   ├── __init__.py
│   ├── session_store.py        # In-memory store [NEW]
│   ├── bot_runner.py           # Pipeline lifecycle [NEW]
│   └── intake_extractor.py     # Data extraction [NEW]
└── voice/
    ├── runner.py               # Pipeline orchestrator [NEW]
    ├── handlers.py             # Event callbacks [NEW]
    ├── pipeline_flow.py        # [EXISTS - may update]
    ├── context.py              # [EXISTS]
    ├── stt.py                  # [EXISTS]
    ├── tts.py                  # [EXISTS]
    ├── vad.py                  # [EXISTS]
    ├── room.py                 # [EXISTS]
    ├── transport.py            # [EXISTS]
    └── llm/
        ├── service.py          # [EXISTS]
        └── prompts.py          # [EXISTS - may update]

medvoice-assistant/src/
├── lib/
│   ├── api.ts                  # Backend client [NEW]
│   ├── daily.ts                # Daily.co helper [NEW]
│   └── utils.ts                # [EXISTS]
├── pages/
│   ├── Index.tsx               # [EXISTS - minor update]
│   ├── VoiceIntake.tsx         # [EXISTS - major update]
│   ├── Results.tsx             # [EXISTS - major update]
│   └── ChatIntake.tsx          # [EXISTS - skip for MVP]
└── components/                  # [EXISTS]

docs/
├── plan.md                     # This file
├── setup.md                    # Environment setup [NEW]
└── demo_script.md              # Demo walkthrough [NEW]
```

---

## What We're NOT Building

| Feature | Why Skip |
|---------|----------|
| Database/PostgreSQL | In-memory dict is fine for demo |
| User authentication | No accounts needed for demo |
| Appointment booking | Out of scope - mock if needed |
| Admin portal | Not showcasing this |
| Chat fallback | Voice-only keeps demo focused |
| Multi-language | English-only for MVP |
| Persistent history | Sessions are ephemeral |

---

## Success Criteria

1. **Works end-to-end**: Click start → speak → see results
2. **Voice quality**: Clear STT recognition, natural TTS responses
3. **Structured output**: Intake data extracted as JSON
4. **Error resilience**: Graceful handling of common failures
5. **Demo-able**: Can show in 2-3 minutes to interviewer

---

## Phase Dependencies

```
Phase 1 (Backend API)
    │
    ▼
Phase 2 (Voice Pipeline)
    │
    ▼
Phase 3 (Frontend Integration)
    │
    ▼
Phase 4 (Polish)
```

Each phase builds on the previous. Complete in order.

---

## Quick Start Commands

```bash
# Backend (from project root)
cd backend
uv sync
python -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd medvoice-assistant
npm install
npm run dev

# Required environment variables (.env)
DEEPGRAM_API_KEY=your_key
GOOGLE_API_KEY=your_key
DAILY_API_KEY=your_key
```
