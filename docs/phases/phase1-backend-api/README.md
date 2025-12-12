# Phase 1: Backend API Foundation

**Goal**: Create minimal API to manage sessions and connect voice pipeline
**Estimated effort**: 4-6 hours

---

## Overview

This phase establishes the FastAPI backend with session management. No database - just in-memory storage for demo purposes.

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI App                       │
├─────────────────────────────────────────────────────┤
│  POST /api/sessions/     → Create session + room    │
│  GET  /api/sessions/{id} → Get session state        │
│  DELETE /api/sessions/{id} → End session            │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              SessionStore (In-Memory)                │
│  Dict[session_id, SessionState]                      │
└─────────────────────────────────────────────────────┘
```

---

## Files to Create

### 1. `backend/app/services/session_store.py`

In-memory session storage with thread-safe operations.

**Interface**:
```python
class SessionStore:
    async def create(self, room_url: str) -> SessionState
    async def get(self, session_id: str) -> SessionState | None
    async def update(self, session_id: str, **kwargs) -> SessionState
    async def delete(self, session_id: str) -> bool
    async def cleanup_expired(self, max_age_seconds: int = 3600) -> int
```

**Requirements**:
- Generate UUID for session_id
- Store creation timestamp
- Thread-safe (asyncio.Lock)
- Auto-cleanup old sessions (optional for MVP)

---

### 2. `backend/app/routes/sessions.py`

Session management endpoints.

**Endpoints**:

```python
@router.post("/", response_model=CreateSessionResponse)
async def create_session():
    """
    1. Create Daily.co room (use existing room.py)
    2. Create session in store
    3. Return session_id + room_url
    """

@router.get("/{session_id}", response_model=SessionState)
async def get_session(session_id: str):
    """
    Return current session state or 404
    """

@router.delete("/{session_id}")
async def end_session(session_id: str):
    """
    Mark session as ended, cleanup resources
    """
```

**Response Models** (use existing from `models/messages.py`):
- `CreateSessionResponse`: session_id, room_url, status
- `SessionState`: full session state

---

### 3. `backend/app/routes/__init__.py`

Router aggregation.

```python
from fastapi import APIRouter
from .sessions import router as sessions_router

api_router = APIRouter(prefix="/api")
api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
```

---

### 4. `backend/app/main.py`

FastAPI application entry point.

**Structure**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_settings
from .routes import api_router
from .services.session_store import session_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing needed for MVP
    yield
    # Shutdown: cleanup sessions
    await session_store.cleanup_all()

app = FastAPI(
    title="MedVoice API",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## Verification Steps

### 1. Run the server
```bash
cd backend
uv sync
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Test health endpoint
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

### 3. Test session creation
```bash
curl -X POST http://localhost:8000/api/sessions/
# Expected: {"session_id": "uuid", "room_url": "https://...", "status": "ACTIVE"}
```

### 4. Test session retrieval
```bash
curl http://localhost:8000/api/sessions/{session_id}
# Expected: Full session state JSON
```

---

## Dependencies

Existing files used:
- `backend/app/config.py` - Settings with API keys
- `backend/app/voice/room.py` - Daily.co room creation
- `backend/app/models/messages.py` - SessionState, CreateSessionResponse

---

## Edge Cases to Handle

1. **Daily.co API failure**: Return 503 with error message
2. **Session not found**: Return 404
3. **Invalid session_id format**: Return 400
4. **Rate limiting**: Optional for MVP, but consider for production

---

## Checklist

- [ ] Create `services/session_store.py`
- [ ] Create `routes/sessions.py`
- [ ] Create `routes/__init__.py`
- [ ] Create `main.py`
- [ ] Test all endpoints manually
- [ ] Add basic error handling
- [ ] Verify CORS works with frontend origin

---

## Next Phase

Once endpoints are working, proceed to **Phase 2: Voice Pipeline Integration** to connect the voice bot to sessions.
