# Phase 3: Frontend Integration

**Goal**: Connect React UI to real backend, enable voice interaction
**Estimated effort**: 4-6 hours
**Depends on**: Phase 2 complete

---

## Overview

Replace mock implementations with real backend integration:

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                            │
├─────────────────────────────────────────────────────────────┤
│  Index.tsx        → Start button creates session            │
│  VoiceIntake.tsx  → Joins Daily room, shows live status     │
│  Results.tsx      → Fetches and displays intake data        │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│   REST API Client   │         │   Daily.co Client   │
│   /api/sessions/*   │         │   WebRTC Audio      │
└─────────────────────┘         └─────────────────────┘
```

---

## Files to Create

### 1. `medvoice-assistant/src/lib/api.ts`

Type-safe API client for backend.

```typescript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface CreateSessionResponse {
  session_id: string;
  room_url: string;
  token: string;
  status: 'ACTIVE' | 'COMPLETE' | 'ABANDONED' | 'FAILED';
}

export interface SessionState {
  session_id: string;
  status: string;
  intake_data: IntakeData | null;
  conversation_history: Message[];
  created_at: string;
  error: string | null;
}

export interface IntakeData {
  demographics: Demographics | null;
  visit: VisitInfo | null;
  medical_history: MedicalHistory | null;
  medications: Medication[];
  allergies: Allergy[];
}

export async function createSession(): Promise<CreateSessionResponse> {
  const response = await fetch(`${API_BASE}/api/sessions/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to create session: ${response.statusText}`);
  }

  return response.json();
}

export async function getSession(sessionId: string): Promise<SessionState> {
  const response = await fetch(`${API_BASE}/api/sessions/${sessionId}`);

  if (!response.ok) {
    throw new Error(`Failed to get session: ${response.statusText}`);
  }

  return response.json();
}

export async function endSession(sessionId: string): Promise<void> {
  await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
}
```

---

### 2. `medvoice-assistant/src/lib/daily.ts`

Daily.co client wrapper.

```typescript
import DailyIframe, { DailyCall } from '@daily-co/daily-js';

export interface DailyConfig {
  roomUrl: string;
  token: string;
  onJoined?: () => void;
  onLeft?: () => void;
  onError?: (error: Error) => void;
  onParticipantJoined?: (participant: any) => void;
  onParticipantLeft?: (participant: any) => void;
}

export class DailyClient {
  private call: DailyCall | null = null;

  async join(config: DailyConfig): Promise<void> {
    this.call = DailyIframe.createCallObject();

    this.call.on('joined-meeting', () => config.onJoined?.());
    this.call.on('left-meeting', () => config.onLeft?.());
    this.call.on('error', (e) => config.onError?.(new Error(e.errorMsg)));
    this.call.on('participant-joined', (e) => config.onParticipantJoined?.(e));
    this.call.on('participant-left', (e) => config.onParticipantLeft?.(e));

    await this.call.join({
      url: config.roomUrl,
      token: config.token,
    });
  }

  async leave(): Promise<void> {
    if (this.call) {
      await this.call.leave();
      this.call.destroy();
      this.call = null;
    }
  }

  async setMicEnabled(enabled: boolean): Promise<void> {
    await this.call?.setLocalAudio(enabled);
  }

  isMicEnabled(): boolean {
    return this.call?.localAudio() ?? false;
  }
}

export const dailyClient = new DailyClient();
```

---

### 3. `medvoice-assistant/src/hooks/useVoiceSession.ts`

React hook for managing voice session state.

```typescript
import { useState, useCallback, useEffect } from 'react';
import { createSession, getSession, endSession, SessionState } from '@/lib/api';
import { dailyClient } from '@/lib/daily';

export type SessionStatus = 'idle' | 'connecting' | 'active' | 'processing' | 'complete' | 'error';

export function useVoiceSession() {
  const [status, setStatus] = useState<SessionStatus>('idle');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [botJoined, setBotJoined] = useState(false);

  const start = useCallback(async () => {
    try {
      setStatus('connecting');
      setError(null);

      // Create session on backend
      const session = await createSession();
      setSessionId(session.session_id);

      // Join Daily room
      await dailyClient.join({
        roomUrl: session.room_url,
        token: session.token,
        onJoined: () => setStatus('active'),
        onLeft: () => setStatus('complete'),
        onError: (e) => {
          setError(e.message);
          setStatus('error');
        },
        onParticipantJoined: (p) => {
          // Bot joins as a participant
          if (p.participant?.user_name === 'MedVoice Bot') {
            setBotJoined(true);
          }
        },
        onParticipantLeft: (p) => {
          if (p.participant?.user_name === 'MedVoice Bot') {
            setBotJoined(false);
            setStatus('processing');
          }
        },
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
      setStatus('error');
    }
  }, []);

  const stop = useCallback(async () => {
    await dailyClient.leave();
    if (sessionId) {
      await endSession(sessionId);
    }
    setStatus('complete');
  }, [sessionId]);

  // Poll for completion when processing
  useEffect(() => {
    if (status !== 'processing' || !sessionId) return;

    const interval = setInterval(async () => {
      const session = await getSession(sessionId);
      if (session.status === 'COMPLETE') {
        setStatus('complete');
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [status, sessionId]);

  return {
    status,
    sessionId,
    error,
    botJoined,
    start,
    stop,
  };
}
```

---

## Update Existing Files

### `medvoice-assistant/src/pages/VoiceIntake.tsx`

Replace mock with real implementation:

```typescript
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useVoiceSession } from '@/hooks/useVoiceSession';
import { Button } from '@/components/ui/button';
import { Mic, MicOff, Phone, PhoneOff } from 'lucide-react';

export default function VoiceIntake() {
  const navigate = useNavigate();
  const { status, sessionId, error, botJoined, start, stop } = useVoiceSession();

  // Auto-start on mount
  useEffect(() => {
    start();
    return () => {
      stop();
    };
  }, []);

  // Navigate to results when complete
  useEffect(() => {
    if (status === 'complete' && sessionId) {
      navigate(`/results?session=${sessionId}`);
    }
  }, [status, sessionId, navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-8">Voice Intake</h1>

      {/* Status indicator */}
      <div className="mb-8">
        {status === 'connecting' && (
          <p className="text-yellow-600">Connecting to voice assistant...</p>
        )}
        {status === 'active' && !botJoined && (
          <p className="text-yellow-600">Waiting for assistant to join...</p>
        )}
        {status === 'active' && botJoined && (
          <p className="text-green-600">Assistant is listening. Please speak.</p>
        )}
        {status === 'processing' && (
          <p className="text-blue-600">Processing your information...</p>
        )}
        {status === 'error' && (
          <p className="text-red-600">Error: {error}</p>
        )}
      </div>

      {/* Visual indicator */}
      <div className={`
        w-32 h-32 rounded-full flex items-center justify-center mb-8
        ${status === 'active' && botJoined ? 'bg-green-100 animate-pulse' : 'bg-gray-100'}
      `}>
        {status === 'active' && botJoined ? (
          <Mic className="w-16 h-16 text-green-600" />
        ) : (
          <MicOff className="w-16 h-16 text-gray-400" />
        )}
      </div>

      {/* End call button */}
      {status === 'active' && (
        <Button variant="destructive" onClick={stop}>
          <PhoneOff className="mr-2" />
          End Session
        </Button>
      )}

      {/* Retry button on error */}
      {status === 'error' && (
        <Button onClick={start}>
          Try Again
        </Button>
      )}
    </div>
  );
}
```

---

### `medvoice-assistant/src/pages/Results.tsx`

Fetch real session data:

```typescript
import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { getSession, SessionState } from '@/lib/api';
import { Button } from '@/components/ui/button';

export default function Results() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('session');
  const [session, setSession] = useState<SessionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setError('No session ID provided');
      setLoading(false);
      return;
    }

    getSession(sessionId)
      .then(setSession)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) {
    return <div className="p-8">Loading results...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <p className="text-red-600 mb-4">Error: {error}</p>
        <Link to="/">
          <Button>Start Over</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-8">Intake Results</h1>

      {/* Intake Summary */}
      {session?.intake_data && (
        <div className="space-y-6">
          {/* Demographics */}
          {session.intake_data.demographics && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Demographics</h2>
              <pre className="bg-gray-100 p-4 rounded">
                {JSON.stringify(session.intake_data.demographics, null, 2)}
              </pre>
            </section>
          )}

          {/* Visit Info */}
          {session.intake_data.visit && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Visit Information</h2>
              <pre className="bg-gray-100 p-4 rounded">
                {JSON.stringify(session.intake_data.visit, null, 2)}
              </pre>
            </section>
          )}

          {/* Medications */}
          {session.intake_data.medications?.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Medications</h2>
              <pre className="bg-gray-100 p-4 rounded">
                {JSON.stringify(session.intake_data.medications, null, 2)}
              </pre>
            </section>
          )}

          {/* Allergies */}
          {session.intake_data.allergies?.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Allergies</h2>
              <pre className="bg-gray-100 p-4 rounded">
                {JSON.stringify(session.intake_data.allergies, null, 2)}
              </pre>
            </section>
          )}
        </div>
      )}

      {/* Raw JSON toggle */}
      <details className="mt-8">
        <summary className="cursor-pointer text-blue-600">View Raw JSON</summary>
        <pre className="bg-gray-900 text-green-400 p-4 rounded mt-2 overflow-auto">
          {JSON.stringify(session, null, 2)}
        </pre>
      </details>

      <div className="mt-8">
        <Link to="/">
          <Button>Start New Intake</Button>
        </Link>
      </div>
    </div>
  );
}
```

---

### `medvoice-assistant/src/pages/Index.tsx`

Add navigation to voice intake:

```typescript
// Add to existing Index.tsx
import { useNavigate } from 'react-router-dom';

// In component:
const navigate = useNavigate();

// Update the CTA button:
<Button size="lg" onClick={() => navigate('/voice-intake')}>
  Start Voice Intake
</Button>
```

---

## Install Dependencies

```bash
cd medvoice-assistant
npm install @daily-co/daily-js
```

---

## Environment Setup

Create `medvoice-assistant/.env`:

```env
VITE_API_URL=http://localhost:8000
```

---

## Verification Steps

### 1. Start backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 2. Start frontend
```bash
cd medvoice-assistant
npm run dev
```

### 3. Test full flow
1. Open http://localhost:5173
2. Click "Start Voice Intake"
3. Allow microphone permission
4. Verify bot greets you
5. Have a conversation
6. Verify results page shows extracted data

---

## Edge Cases

1. **Microphone denied**: Show clear error message with instructions
2. **Backend unavailable**: Timeout and show retry option
3. **Session expired**: Redirect to home with message
4. **Mobile browser**: Test audio permissions on iOS/Android

---

## Checklist

- [ ] Create `lib/api.ts`
- [ ] Create `lib/daily.ts`
- [ ] Create `hooks/useVoiceSession.ts`
- [ ] Update `VoiceIntake.tsx`
- [ ] Update `Results.tsx`
- [ ] Update `Index.tsx`
- [ ] Install Daily.co SDK
- [ ] Test microphone permissions
- [ ] Test full end-to-end flow
- [ ] Test error states

---

## Next Phase

Once frontend integration is complete, proceed to **Phase 4: Polish** for error handling and demo preparation.
