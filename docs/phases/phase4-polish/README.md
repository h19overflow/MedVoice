# Phase 4: Polish & Demo Ready

**Goal**: Make the project demo-worthy for portfolio/interviews
**Estimated effort**: 2-4 hours
**Depends on**: Phase 3 complete

---

## Overview

This phase focuses on reliability, user experience, and demo preparation. No new features - just making what exists work smoothly.

---

## 1. Error Handling Improvements

### Backend Error Responses

Create `backend/app/utils/errors.py`:

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

class MedVoiceException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

class SessionNotFoundError(MedVoiceException):
    def __init__(self, session_id: str):
        super().__init__(f"Session {session_id} not found", 404)

class DailyRoomError(MedVoiceException):
    def __init__(self, detail: str):
        super().__init__(f"Failed to create room: {detail}", 503)

class VoicePipelineError(MedVoiceException):
    def __init__(self, detail: str):
        super().__init__(f"Voice pipeline error: {detail}", 500)
```

Add exception handler in `main.py`:

```python
@app.exception_handler(MedVoiceException)
async def medvoice_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message}
    )
```

### Frontend Error Display

Update error states in `VoiceIntake.tsx`:

```typescript
const ERROR_MESSAGES: Record<string, string> = {
  'microphone': 'Microphone access denied. Please allow microphone access and try again.',
  'network': 'Unable to connect to the server. Please check your internet connection.',
  'timeout': 'Connection timed out. The server may be busy.',
  'default': 'Something went wrong. Please try again.',
};

function getErrorMessage(error: string): string {
  if (error.includes('permission') || error.includes('NotAllowed')) {
    return ERROR_MESSAGES.microphone;
  }
  if (error.includes('fetch') || error.includes('network')) {
    return ERROR_MESSAGES.network;
  }
  return ERROR_MESSAGES.default;
}
```

---

## 2. Loading States

### Skeleton Components

Create `medvoice-assistant/src/components/LoadingSkeleton.tsx`:

```typescript
export function SessionLoadingSkeleton() {
  return (
    <div className="flex flex-col items-center justify-center p-8 animate-pulse">
      <div className="w-32 h-32 rounded-full bg-gray-200 mb-8" />
      <div className="h-4 w-48 bg-gray-200 rounded mb-4" />
      <div className="h-4 w-32 bg-gray-200 rounded" />
    </div>
  );
}

export function ResultsLoadingSkeleton() {
  return (
    <div className="max-w-4xl mx-auto p-8 animate-pulse">
      <div className="h-8 w-48 bg-gray-200 rounded mb-8" />
      <div className="space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i}>
            <div className="h-6 w-32 bg-gray-200 rounded mb-2" />
            <div className="h-24 bg-gray-200 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 3. Accessibility Improvements

### ARIA Labels

```typescript
// VoiceIntake.tsx
<div
  role="status"
  aria-live="polite"
  aria-label={`Voice assistant status: ${status}`}
>
  {/* status content */}
</div>

<button
  aria-label={botJoined ? 'Microphone active, assistant is listening' : 'Waiting for connection'}
>
  {/* mic icon */}
</button>
```

### Keyboard Navigation

```typescript
// Ensure all interactive elements are focusable
<Button
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleAction();
    }
  }}
>
```

---

## 4. Demo Script

Create `docs/demo_script.md`:

```markdown
# MedVoice Demo Script

## Setup Before Demo
1. Ensure backend is running: `python -m uvicorn app.main:app`
2. Ensure frontend is running: `npm run dev`
3. Test microphone works
4. Have browser ready at http://localhost:5173

## Demo Flow (2-3 minutes)

### 1. Introduction (30 seconds)
"This is MedVoice, a voice-first medical intake assistant.
Instead of filling out forms, patients speak naturally
and the AI extracts structured medical information."

### 2. Start Session (30 seconds)
- Click "Start Voice Intake"
- Wait for "Assistant is listening" indicator
- "The system uses Daily.co for real-time audio,
   Deepgram for speech recognition, and Google Gemini
   for natural language understanding."

### 3. Demo Conversation (1-2 minutes)
Sample phrases that work well:

**Greeting response:**
"Hi, my name is John Smith"

**Demographics:**
"I'm 45 years old, my date of birth is March 15th, 1979"

**Chief complaint:**
"I've been having chest pain for the past three days"

**Symptoms:**
"The pain is sharp, about a 7 out of 10, and it gets
worse when I breathe deeply"

**Medical history:**
"I have high blood pressure and type 2 diabetes"

**Medications:**
"I take metformin 500mg twice a day and lisinopril 10mg"

**Allergies:**
"I'm allergic to penicillin - I get a rash"

### 4. Show Results (30 seconds)
- End the session
- Show the Results page
- "The AI extracted all this information into structured
   JSON that can be sent to an EHR system"
- Expand "View Raw JSON" to show the data structure

## Talking Points

**If asked about accuracy:**
"The speech recognition uses Deepgram's nova-2 model,
which handles medical terminology well. The extraction
uses Gemini with specific prompts for medical intake."

**If asked about privacy:**
"In production, this would use HIPAA-compliant services.
For the demo, we're using development endpoints."

**If asked about scaling:**
"The architecture uses Daily.co rooms per session, so
it scales horizontally. Each session is independent."

## Known Limitations (be upfront)
- English only
- Works best in quiet environments
- No authentication in demo
- Sessions are not persisted

## Troubleshooting During Demo

**Mic not working:**
- Check browser permissions
- Try a different browser
- Have a backup recording ready

**Backend error:**
- Check terminal for errors
- Restart uvicorn
- Have screenshots ready as backup

**Bot not responding:**
- Check API keys in .env
- Daily.co quota might be exceeded
- Switch to showing architecture diagram
```

---

## 5. Environment Setup Guide

Create `docs/setup.md`:

```markdown
# MedVoice Local Setup

## Prerequisites
- Python 3.11+
- Node.js 18+
- uv (Python package manager)
- A microphone

## API Keys Required

You'll need accounts and API keys from:

1. **Deepgram** (STT/TTS)
   - Sign up: https://console.deepgram.com/signup
   - Free tier: 12,000 minutes
   - Get API key from dashboard

2. **Google AI** (Gemini LLM)
   - Sign up: https://makersuite.google.com/app/apikey
   - Free tier available
   - Create API key

3. **Daily.co** (WebRTC)
   - Sign up: https://dashboard.daily.co/signup
   - Free tier: 10,000 minutes
   - Get API key from Developers tab

## Setup Steps

### 1. Clone and navigate
```bash
git clone <repo-url>
cd MedVoice
```

### 2. Backend setup
```bash
cd backend
uv sync
```

Create `backend/.env`:
```env
DEEPGRAM_API_KEY=your_deepgram_key
GOOGLE_API_KEY=your_google_key
DAILY_API_KEY=your_daily_key
DEBUG=true
```

### 3. Frontend setup
```bash
cd medvoice-assistant
npm install
```

Create `medvoice-assistant/.env`:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Run the application

Terminal 1 (Backend):
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Terminal 2 (Frontend):
```bash
cd medvoice-assistant
npm run dev
```

### 5. Open the app
Navigate to http://localhost:5173

## Troubleshooting

### "CORS error"
- Ensure backend is running on port 8000
- Check CORS_ORIGINS in backend config

### "Microphone not detected"
- Use Chrome or Firefox (Safari has issues)
- Check browser permissions
- Try: chrome://settings/content/microphone

### "Failed to create room"
- Verify DAILY_API_KEY is correct
- Check Daily.co dashboard for quota

### "No response from bot"
- Check backend logs for errors
- Verify GOOGLE_API_KEY is valid
- Check Deepgram key permissions

### "STT not transcribing"
- Speak clearly, close to microphone
- Reduce background noise
- Check Deepgram dashboard for usage
```

---

## 6. Final Checklist

### Functionality
- [ ] Session creation works reliably
- [ ] Voice connection establishes quickly (<3s)
- [ ] STT transcribes accurately
- [ ] Bot responds naturally
- [ ] Intake extraction produces valid JSON
- [ ] Results page displays all data
- [ ] Session cleanup works

### Error Handling
- [ ] Microphone permission denied → clear message
- [ ] Backend offline → timeout and retry option
- [ ] Daily.co failure → graceful error
- [ ] Extraction failure → shows partial data

### User Experience
- [ ] Loading states for all async operations
- [ ] Visual feedback for speaking/listening
- [ ] Clear status messages
- [ ] Mobile-friendly layout

### Demo Readiness
- [ ] Demo script practiced
- [ ] All API keys working
- [ ] Backup screenshots/video ready
- [ ] Known limitations documented

---

## Optional Enhancements (Time Permitting)

### Visual Waveform
Add audio visualization during recording:
```bash
npm install wavesurfer.js
```

### Conversation Transcript
Show live transcript during conversation in a sidebar.

### Export Options
Add buttons to export intake data as PDF or copy JSON.

---

## Done!

At this point you have a demo-ready voice agent that:
1. Creates real-time voice sessions
2. Conducts natural medical intake conversations
3. Extracts structured data
4. Displays results cleanly

This showcases: **voice AI, real-time communication, NLU, structured extraction** - all the impressive parts for a portfolio project.
