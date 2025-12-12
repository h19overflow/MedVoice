# Phase 2: Voice Pipeline Integration

**Goal**: Connect existing voice components into a runnable pipeline tied to sessions
**Estimated effort**: 4-6 hours
**Depends on**: Phase 1 complete

---

## Overview

Wire up the Pipecat voice pipeline so it:
1. Starts when a session is created
2. Joins the Daily.co room
3. Handles voice conversation
4. Extracts intake data on completion
5. Updates session state

```
┌─────────────────────────────────────────────────────────────┐
│                      Bot Runner                              │
│  Manages lifecycle: start → run → extract → cleanup         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Pipecat Pipeline                           │
│  Transport → VAD → STT → LLM Context → TTS → Transport      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Intake Extractor                           │
│  Parse conversation → Extract structured data → Validate    │
└─────────────────────────────────────────────────────────────┘
```

---

## Files to Create

### 1. `backend/app/services/bot_runner.py`

Manages voice bot lifecycle for a session.

**Interface**:
```python
class BotRunner:
    def __init__(self, session_id: str, room_url: str):
        self.session_id = session_id
        self.room_url = room_url
        self.task: asyncio.Task | None = None
        self.conversation_history: list[dict] = []

    async def start(self) -> None:
        """Start the voice bot in background task"""

    async def stop(self) -> None:
        """Gracefully stop the bot"""

    def on_conversation_end(self, history: list[dict]) -> None:
        """Callback when conversation completes"""
```

**Implementation Notes**:
- Use `asyncio.create_task()` to run pipeline in background
- Store reference in a global dict: `active_bots[session_id] = runner`
- Clean up on session end or error

---

### 2. `backend/app/voice/runner.py`

Actual pipeline construction and execution.

**Interface**:
```python
async def run_voice_pipeline(
    room_url: str,
    token: str,
    on_message: Callable[[str, str], None],  # role, content
    on_complete: Callable[[], None],
    on_error: Callable[[Exception], None],
) -> None:
    """
    Build and run the Pipecat pipeline.

    Uses existing factories:
    - create_transport() from voice/transport.py
    - create_stt_service() from voice/stt.py
    - create_tts_service() from voice/tts.py
    - create_vad() from voice/vad.py
    - create_llm_service() from voice/llm/service.py
    - create_llm_context() from voice/context.py
    """
```

**Pipeline Flow**:
```python
pipeline = Pipeline([
    transport.input(),      # Audio from Daily
    vad,                    # Voice activity detection
    stt,                    # Speech to text
    llm_context,            # Conversation context
    llm,                    # Gemini response
    tts,                    # Text to speech
    transport.output(),     # Audio to Daily
])
```

---

### 3. `backend/app/services/intake_extractor.py`

Extract structured intake data from conversation.

**Interface**:
```python
async def extract_intake_data(
    conversation_history: list[dict],
    llm_service: Any,  # Gemini client
) -> IntakeData:
    """
    Send conversation to LLM with extraction prompt.
    Parse response into IntakeData model.
    """
```

**Extraction Prompt**:
```
Given the following medical intake conversation, extract structured data.
Return JSON matching this schema: {IntakeData.model_json_schema()}

Conversation:
{formatted_history}

Extract all mentioned: demographics, symptoms, medical history, medications, allergies.
If information wasn't provided, use null.
```

**Fallback**: If extraction fails, return partial data with `extraction_failed: true`

---

### 4. `backend/app/voice/handlers.py`

Event handlers for pipeline events.

**Handlers**:
```python
class PipelineHandlers:
    def __init__(self, session_id: str, session_store: SessionStore):
        self.session_id = session_id
        self.messages: list[dict] = []

    async def on_user_speech(self, text: str) -> None:
        """Called when STT produces transcript"""
        self.messages.append({"role": "user", "content": text})
        await self.session_store.update(
            self.session_id,
            last_user_message=text
        )

    async def on_bot_speech(self, text: str) -> None:
        """Called when LLM produces response"""
        self.messages.append({"role": "assistant", "content": text})

    async def on_complete(self) -> None:
        """Called when conversation ends"""
        intake_data = await extract_intake_data(self.messages)
        await self.session_store.update(
            self.session_id,
            status=SessionStatus.COMPLETE,
            intake_data=intake_data,
            conversation_history=self.messages
        )

    async def on_error(self, error: Exception) -> None:
        """Called on pipeline error"""
        await self.session_store.update(
            self.session_id,
            status=SessionStatus.FAILED,
            error=str(error)
        )
```

---

## Update Existing Files

### `backend/app/routes/sessions.py`

Add bot startup to session creation:

```python
@router.post("/")
async def create_session():
    room_url, token = await create_daily_room()
    session = await session_store.create(room_url=room_url)

    # Start bot in background
    runner = BotRunner(session.session_id, room_url, token)
    await runner.start()
    active_bots[session.session_id] = runner

    return CreateSessionResponse(
        session_id=session.session_id,
        room_url=room_url,
        token=token,  # Client needs this to join
        status=session.status
    )
```

---

## Verification Steps

### 1. Create session and verify bot starts
```bash
curl -X POST http://localhost:8000/api/sessions/
# Check logs for "Bot started for session {id}"
```

### 2. Join Daily room manually
- Go to returned `room_url` in browser
- Verify bot joins and greets you

### 3. Have a test conversation
- Speak symptoms/info to the bot
- Verify STT works (check logs)
- Verify bot responds (TTS)

### 4. Check extraction
```bash
curl http://localhost:8000/api/sessions/{id}
# Should show intake_data populated after conversation
```

---

## Pipecat Integration Points

Use these existing factories from `backend/app/voice/`:

| Factory | File | Returns |
|---------|------|---------|
| `create_stt_service()` | `stt.py` | DeepgramSTTService |
| `create_tts_service()` | `tts.py` | DeepgramTTSService |
| `create_vad()` | `vad.py` | SileroVADAnalyzer |
| `create_llm_service()` | `llm/service.py` | GoogleLLMService |
| `create_llm_context()` | `context.py` | OpenAILLMContext |
| `create_transport()` | `transport.py` | DailyTransport |
| `create_daily_room()` | `room.py` | (room_url, token) |

---

## Edge Cases

1. **User disconnects early**: Detect via Daily events, mark session abandoned
2. **Bot crashes**: Catch exceptions, update session status, log error
3. **STT fails repeatedly**: Fallback message "I didn't catch that"
4. **Long silence**: VAD timeout → prompt user or end session
5. **Extraction fails**: Store raw conversation, mark extraction_failed

---

## Checklist

- [ ] Create `services/bot_runner.py`
- [ ] Create `voice/runner.py`
- [ ] Create `services/intake_extractor.py`
- [ ] Create `voice/handlers.py`
- [ ] Update session creation to start bot
- [ ] Test end-to-end voice conversation
- [ ] Verify intake extraction works
- [ ] Add error handling for all failure modes

---

## Next Phase

Once voice pipeline works end-to-end, proceed to **Phase 3: Frontend Integration** to connect the React UI.
