# MedVoice MVP - Product Requirements Document

**Version:** 1.0  
**Author:** Hamza Khaled  
**Date:** December 2025  
**Status:** Draft  

---

## 1. Overview

### 1.1 Problem Statement

Medical clinics waste 15-20 minutes per patient on intake paperwork. Patients fill out repetitive forms, handwriting is illegible, and staff manually enter data into systems. This creates:

- Poor patient experience (waiting room frustration)
- Staff inefficiency (data entry instead of patient care)
- Data quality issues (transcription errors, incomplete forms)
- Accessibility barriers (elderly, visually impaired patients struggle with forms)

### 1.2 Solution

MedVoice is an AI-powered voice agent that conducts patient intake conversations. Patients speak naturally, and the system extracts structured medical data ready for clinical use.

### 1.3 MVP Goal

**Build a working voice intake demo in 2 weeks** that:
- Conducts a complete intake conversation via voice
- Extracts structured patient data
- Generates a summary document
- Demonstrates portfolio-worthy voice AI + RAG skills

### 1.4 Success Criteria

| Metric | Target |
|--------|--------|
| End-to-end latency | < 800ms |
| Intake completion rate | > 70% (of started sessions) |
| Data extraction accuracy | > 85% (spot-checked) |
| Demo duration | 3-5 minutes for full intake |

---

## 2. Scope

### 2.1 In Scope (MVP)

| Feature | Priority | Notes |
|---------|----------|-------|
| Voice conversation (English) | P0 | Core functionality |
| Basic intake flow (5 sections) | P0 | Demographics, Visit, History, Meds, Allergies |
| Structured data extraction | P0 | JSON output |
| Text summary generation | P0 | Human-readable summary |
| Web-based voice interface | P0 | Browser microphone access |
| Single clinic configuration | P1 | Hardcoded prompts |
| Conversation transcript | P1 | For debugging/demo |

### 2.2 Out of Scope (MVP)

| Feature | Reason | Future Version |
|---------|--------|----------------|
| Arabic language | Complexity | v1.1 |
| Chat mode (text) | Focus on voice first | v1.1 |
| RAG customization | Nice-to-have | v1.2 |
| Admin panel | Not needed for demo | v1.2 |
| PDF generation | JSON is sufficient | v1.1 |
| User authentication | Demo only | v2.0 |
| HIPAA compliance | Demo only | v2.0 |
| EHR integration | Mock only | v2.0 |
| Mobile app | Web only | v2.0 |
| Multi-clinic support | Single config | v2.0 |

### 2.3 Assumptions

1. User has a working microphone and modern browser
2. User speaks clear English (not heavy accents for MVP)
3. Stable internet connection for real-time audio
4. Demo environment only (no real patient data)

### 2.4 Constraints

1. **Budget:** Free tier APIs only ($200 Deepgram, free Gemini)
2. **Timeline:** 2 weeks to working demo
3. **Team:** Solo developer
4. **Infrastructure:** Local development + simple cloud deploy

---

## 3. User Stories

### 3.1 Primary User: Patient

```
US-001: Start Voice Intake
AS A patient
I WANT TO start an intake conversation by clicking a button
SO THAT I can complete my intake without filling forms

Acceptance Criteria:
- [ ] Single "Start Intake" button visible on page
- [ ] Microphone permission requested on click
- [ ] Agent greets me within 2 seconds of starting
- [ ] Clear visual indicator that agent is listening
```

```
US-002: Provide Information by Voice
AS A patient
I WANT TO speak my information naturally
SO THAT I don't have to type or write

Acceptance Criteria:
- [ ] Agent understands my spoken responses
- [ ] Agent asks clarifying questions if unclear
- [ ] I can correct mistakes by saying "no, I said..."
- [ ] Agent confirms critical info (allergies) back to me
```

```
US-003: Complete Full Intake
AS A patient
I WANT TO answer all required intake questions
SO THAT my information is ready for my appointment

Acceptance Criteria:
- [ ] Agent collects: name, DOB, contact, visit reason, symptoms, 
      medical history, medications, allergies
- [ ] Agent tells me when we're done
- [ ] Total conversation takes < 5 minutes
- [ ] I receive confirmation of what was collected
```

```
US-004: Handle Mistakes
AS A patient
I WANT TO correct information if the agent misheard
SO THAT my medical record is accurate

Acceptance Criteria:
- [ ] Agent offers to repeat/confirm critical items
- [ ] I can interrupt and say "wait, that's wrong"
- [ ] Agent gracefully handles corrections
- [ ] Final confirmation step before submission
```

### 3.2 Secondary User: Developer/Demo Viewer

```
US-005: View Extracted Data
AS A demo viewer
I WANT TO see the structured data extracted from the conversation
SO THAT I can verify the system works correctly

Acceptance Criteria:
- [ ] JSON output visible after conversation
- [ ] Human-readable summary generated
- [ ] Conversation transcript available
- [ ] Can see what fields were extracted vs missed
```

```
US-006: Monitor Conversation
AS A developer
I WANT TO see real-time transcription and state
SO THAT I can debug issues

Acceptance Criteria:
- [ ] Live transcript panel (what patient said)
- [ ] Current state indicator (which section)
- [ ] Latency metrics visible
- [ ] Error states clearly shown
```

---

## 4. Functional Requirements

### 4.1 Voice Pipeline

| ID | Requirement | Priority |
|----|-------------|----------|
| VP-001 | System shall capture audio from browser microphone | P0 |
| VP-002 | System shall detect voice activity (VAD) to know when user is speaking | P0 |
| VP-003 | System shall transcribe speech to text in < 300ms | P0 |
| VP-004 | System shall generate contextual responses via LLM | P0 |
| VP-005 | System shall convert response text to speech in < 200ms TTFB | P0 |
| VP-006 | System shall play audio response to user | P0 |
| VP-007 | System shall handle user interruptions (barge-in) | P1 |
| VP-008 | System shall handle silence/no-response gracefully | P1 |

### 4.2 Intake Flow

| ID | Requirement | Priority |
|----|-------------|----------|
| IF-001 | System shall greet patient and explain the process | P0 |
| IF-002 | System shall collect demographics (name, DOB, phone) | P0 |
| IF-003 | System shall collect visit reason and symptoms | P0 |
| IF-004 | System shall collect medical history | P0 |
| IF-005 | System shall collect current medications | P0 |
| IF-006 | System shall collect allergies with extra confirmation | P0 |
| IF-007 | System shall provide final summary and confirmation | P0 |
| IF-008 | System shall allow skipping optional fields | P1 |
| IF-009 | System shall handle "I don't know" responses | P1 |

### 4.3 Data Extraction

| ID | Requirement | Priority |
|----|-------------|----------|
| DE-001 | System shall extract structured data from conversation | P0 |
| DE-002 | System shall output JSON with all collected fields | P0 |
| DE-003 | System shall generate human-readable summary | P0 |
| DE-004 | System shall flag missing required fields | P1 |
| DE-005 | System shall normalize date formats | P1 |
| DE-006 | System shall normalize medication names (best effort) | P2 |

### 4.4 User Interface

| ID | Requirement | Priority |
|----|-------------|----------|
| UI-001 | System shall display "Start Intake" button | P0 |
| UI-002 | System shall show listening/speaking/processing states | P0 |
| UI-003 | System shall display real-time transcript | P0 |
| UI-004 | System shall show current intake section | P1 |
| UI-005 | System shall display final results (JSON + summary) | P0 |
| UI-006 | System shall work on Chrome desktop | P0 |
| UI-007 | System shall be responsive (mobile-friendly) | P2 |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Requirement |
|--------|-------------|
| End-to-end latency | < 800ms (user stops speaking → agent starts responding) |
| STT latency | < 300ms |
| LLM latency (TTFB) | < 400ms |
| TTS latency (TTFB) | < 200ms |
| Concurrent users | 1 (demo only) |

### 5.2 Reliability

| Metric | Requirement |
|--------|-------------|
| Uptime | Best effort (demo) |
| Error recovery | Graceful degradation with user message |
| Session persistence | Not required (single session) |

### 5.3 Security

| Requirement | Notes |
|-------------|-------|
| No real patient data | Demo only, use fake data |
| API keys secured | Environment variables, not in code |
| No data persistence | In-memory only for MVP |

---

## 6. Technical Architecture

### 6.1 System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      BROWSER CLIENT                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Microphone │  │   Speaker   │  │    React UI         │  │
│  │   Input     │  │   Output    │  │  - Start Button     │  │
│  └──────┬──────┘  └──────▲──────┘  │  - Transcript       │  │
│         │                │         │  - State Indicator  │  │
│         ▼                │         │  - Results Panel    │  │
│  ┌─────────────────────────────┐   └─────────────────────┘  │
│  │     Daily.co WebRTC SDK     │                            │
│  └──────────────┬──────────────┘                            │
└─────────────────┼───────────────────────────────────────────┘
                  │ WebRTC Audio Stream
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    PIPECAT SERVER                            │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Silero  │───▶│ Deepgram │───▶│  Gemini  │              │
│  │   VAD    │    │  Nova-2  │    │  2.5 FL  │              │
│  │          │    │   STT    │    │   LLM    │              │
│  └──────────┘    └──────────┘    └────┬─────┘              │
│                                       │                     │
│                                       ▼                     │
│                              ┌──────────────┐               │
│                              │   Intake     │               │
│                              │  Processor   │               │
│                              │ (State Mgmt) │               │
│                              └──────┬───────┘               │
│                                     │                       │
│                                     ▼                       │
│                              ┌──────────────┐               │
│                              │  Deepgram    │               │
│                              │   Aura TTS   │               │
│                              └──────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Tech Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Voice Framework | Pipecat | Best open-source voice agent framework |
| WebRTC Transport | Daily.co | Built by Pipecat team, free tier |
| STT | Deepgram Nova-2 | Fast, accurate, $200 free credit |
| TTS | Deepgram Aura | Same provider, low latency |
| LLM | Gemini 2.5 Flash-Lite | Free tier, fast, good quality |
| VAD | Silero | Best open-source VAD |
| Backend | FastAPI | Async Python, fast |
| Frontend | React + Vite | Fast dev, simple |
| Styling | Tailwind CSS | Rapid UI development |

### 6.3 Data Flow

```
1. User clicks "Start Intake"
2. Browser requests microphone permission
3. Daily.co WebRTC connection established
4. Agent speaks greeting (TTS → Audio out)
5. User speaks response (Audio in → VAD → STT)
6. Transcribed text sent to Intake Processor
7. Intake Processor:
   a. Updates conversation state
   b. Extracts any data from response
   c. Generates next question via Gemini
8. Response converted to speech (TTS)
9. Audio played to user
10. Repeat 5-9 until intake complete
11. Final summary generated and displayed
```

---

## 7. Intake Flow Specification

### 7.1 State Machine

```
START
  │
  ▼
GREETING ──────────────────────────────────────────┐
  │ "Hi! I'm MedVoice... What's your full name?"   │
  ▼                                                │
DEMOGRAPHICS                                       │
  │ Name → DOB → Phone                             │
  │ (3 sub-questions)                              │
  ▼                                                │
VISIT_REASON                                       │
  │ "What brings you in today?"                    │
  │ → Follow-up on symptoms                        │
  │ → Duration                                     │
  ▼                                                │
MEDICAL_HISTORY                                    │ Can say
  │ "Any chronic conditions?"                      │ "go back"
  │ → Surgeries                                    │ to revisit
  │ → Hospitalizations                             │
  ▼                                                │
MEDICATIONS                                        │
  │ "Taking any medications?"                      │
  │ → List them                                    │
  ▼                                                │
ALLERGIES ⚠️ CRITICAL                              │
  │ "Any drug allergies?"                          │
  │ → Food allergies                               │
  │ → MUST CONFIRM                                 │
  ▼                                                │
CONFIRMATION ◄─────────────────────────────────────┘
  │ "Let me confirm what I have..."
  │ → Read back key info
  │ → "Is this correct?"
  ▼
COMPLETE
  │ "Thank you! Your info is ready."
  │ → Display results
  ▼
END
```

### 7.2 Section Details

#### GREETING
```
Agent: "Hi! I'm MedVoice, your virtual intake assistant. I'll ask you 
        a few questions to prepare for your visit today. This should 
        take about 3 to 4 minutes. Let's start with your full name?"
```

#### DEMOGRAPHICS
| Field | Question | Validation | Required |
|-------|----------|------------|----------|
| full_name | "What's your full name?" | Non-empty | Yes |
| date_of_birth | "And your date of birth?" | Valid date | Yes |
| phone | "Best phone number to reach you?" | 10+ digits | Yes |

#### VISIT_REASON
| Field | Question | Validation | Required |
|-------|----------|------------|----------|
| chief_complaint | "What brings you in today?" | Non-empty | Yes |
| symptoms | "Can you describe your symptoms?" | List extraction | Yes |
| duration | "How long have you had these symptoms?" | Duration parse | No |
| severity | "On a scale of 1-10, how severe?" | 1-10 | No |

#### MEDICAL_HISTORY
| Field | Question | Validation | Required |
|-------|----------|------------|----------|
| conditions | "Any chronic conditions like diabetes or high blood pressure?" | List | No |
| surgeries | "Any past surgeries?" | List | No |
| hospitalizations | "Any hospitalizations in the past year?" | List | No |

#### MEDICATIONS
| Field | Question | Validation | Required |
|-------|----------|------------|----------|
| medications | "Are you currently taking any medications?" | List | No |
| (follow-up) | "What's the dosage?" | Per medication | No |

#### ALLERGIES (Critical Section)
| Field | Question | Validation | Required |
|-------|----------|------------|----------|
| drug_allergies | "Do you have any drug allergies?" | List + confirm | Yes |
| food_allergies | "Any food allergies?" | List | No |
| reactions | "What kind of reaction do you have?" | Text | If allergies |

**Special handling:** 
- If "no allergies" → "Just to confirm, you have NO known drug allergies?"
- If allergies listed → Read them back and confirm

#### CONFIRMATION
```
Agent: "Great, let me confirm what I have. Your name is [NAME], 
        date of birth [DOB]. You're coming in for [REASON]. 
        You mentioned [SYMPTOMS]. 
        
        For medications, I have [MEDS or 'none listed'].
        
        And importantly, for allergies: [ALLERGIES or 'no known allergies'].
        
        Does all of that sound correct?"
```

---

## 8. Data Models

### 8.1 Intake Data (Output)

```json
{
  "session_id": "uuid",
  "timestamp": "2025-12-07T10:30:00Z",
  "status": "complete",
  
  "demographics": {
    "full_name": "John Smith",
    "date_of_birth": "1985-03-15",
    "phone": "555-123-4567",
    "email": null
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
    {
      "name": "lisinopril",
      "dosage": "10mg daily"
    }
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

### 8.2 Conversation Transcript

```json
{
  "session_id": "uuid",
  "turns": [
    {
      "turn_id": 1,
      "speaker": "agent",
      "text": "Hi! I'm MedVoice...",
      "timestamp": "2025-12-07T10:30:00Z",
      "state": "GREETING"
    },
    {
      "turn_id": 2,
      "speaker": "patient",
      "text": "Hi, my name is John Smith",
      "timestamp": "2025-12-07T10:30:05Z",
      "state": "DEMOGRAPHICS",
      "extracted": {"full_name": "John Smith"}
    }
  ]
}
```

---

## 9. UI Wireframes

### 9.1 Main Screen (Idle)

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                     🏥 MedVoice                         │
│              AI-Powered Patient Intake                  │
│                                                         │
│         ┌─────────────────────────────────┐            │
│         │                                 │            │
│         │      [ 🎤 Start Intake ]        │            │
│         │                                 │            │
│         └─────────────────────────────────┘            │
│                                                         │
│           Click to begin your intake                    │
│           conversation with our AI assistant            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 9.2 Active Conversation

```
┌─────────────────────────────────────────────────────────┐
│  🏥 MedVoice              Section: VISIT_REASON  [3/6]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  │         🔊 Agent is speaking...                 │   │
│  │                                                 │   │
│  │    "What brings you in to the clinic today?"   │   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Transcript                                     │   │
│  │  ─────────────────────────────────────────────  │   │
│  │  🤖 Hi! I'm MedVoice... What's your name?      │   │
│  │  👤 My name is John Smith                       │   │
│  │  🤖 Nice to meet you John. Date of birth?      │   │
│  │  👤 March 15th, 1985                           │   │
│  │  🤖 And your phone number?                     │   │
│  │  👤 555-123-4567                               │   │
│  │  🤖 What brings you in today?                  │   │
│  │  █                                              │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│           [ 🎤 Listening... ]    [ End Session ]        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 9.3 Results Screen

```
┌─────────────────────────────────────────────────────────┐
│  🏥 MedVoice                        ✅ Intake Complete  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────┐ ┌─────────────────────────┐   │
│  │ Summary             │ │ JSON Data               │   │
│  ├─────────────────────┤ ├─────────────────────────┤   │
│  │                     │ │ {                       │   │
│  │ Patient: John Smith │ │   "demographics": {     │   │
│  │ DOB: March 15, 1985 │ │     "full_name": "John  │   │
│  │ Phone: 555-123-4567 │ │       Smith",           │   │
│  │                     │ │     "date_of_birth":    │   │
│  │ Chief Complaint:    │ │       "1985-03-15",     │   │
│  │ Persistent headache │ │     ...                 │   │
│  │                     │ │   }                     │   │
│  │ ⚠️ Allergies:       │ │ }                       │   │
│  │ Penicillin (rash)   │ │                         │   │
│  │                     │ │                         │   │
│  └─────────────────────┘ └─────────────────────────┘   │
│                                                         │
│       [ 📋 Copy JSON ]  [ 🔄 Start New ]               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Development Milestones

### Phase 1: Voice Foundation (Days 1-4)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Environment setup, API keys, project scaffold | Running dev environment |
| 2 | Basic Pipecat pipeline (STT → TTS loop) | Echo bot working |
| 3 | Add Gemini LLM, basic conversation | Conversational bot |
| 4 | Integrate Daily.co transport, browser client | Voice in browser |

**Phase 1 Demo:** Talk to bot in browser, it responds contextually

### Phase 2: Intake Logic (Days 5-8)

| Day | Task | Deliverable |
|-----|------|-------------|
| 5 | State machine implementation | Section navigation |
| 6 | Data extraction (Gemini structured output) | JSON extraction |
| 7 | Full intake flow (all sections) | Complete conversation |
| 8 | Confirmation and correction handling | Polish flow |

**Phase 2 Demo:** Complete full intake, see extracted JSON

### Phase 3: UI + Polish (Days 9-12)

| Day | Task | Deliverable |
|-----|------|-------------|
| 9 | React UI scaffold, basic layout | UI shell |
| 10 | Real-time transcript, state display | Live feedback |
| 11 | Results display, JSON/summary view | Output screens |
| 12 | Error handling, edge cases | Robust system |

**Phase 3 Demo:** Full demo-ready application

### Phase 4: Deploy + Document (Days 13-14)

| Day | Task | Deliverable |
|-----|------|-------------|
| 13 | Deploy to cloud (Railway/Render) | Live URL |
| 14 | Documentation, demo video, README | Portfolio ready |

**Final Deliverable:** Deployed app + demo video + documentation

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| High latency (> 1s) | Medium | High | Profile early, optimize STT/TTS provider settings |
| STT accuracy issues | Medium | Medium | Clear speech in demo, show transcript for verification |
| LLM extraction errors | Medium | Medium | Add confirmation step, allow corrections |
| API rate limits | Low | Medium | Monitor usage, cache where possible |
| Browser compatibility | Low | Low | Test Chrome only for MVP |
| Scope creep | High | High | Strict adherence to this PRD |

---

## 12. Open Questions

1. **Q:** Should we persist sessions to a database?  
   **A:** No for MVP. In-memory only. Add persistence in v1.1.

2. **Q:** How do we handle very long symptom descriptions?  
   **A:** Let them talk, extract key points. LLM summarizes.

3. **Q:** What if user gives info out of order?  
   **A:** Accept it, fill in the relevant field, continue with missing items.

4. **Q:** Should we add appointment scheduling?  
   **A:** Out of scope. End with "Your intake is complete, please check in at reception."

---

## 13. Appendix

### A. Sample Conversation Script

```
AGENT: Hi! I'm MedVoice, your virtual intake assistant. I'll ask you 
       a few questions to prepare for your visit today. This should 
       take about 3 to 4 minutes. Let's start - what's your full name?

USER:  My name is John Smith.

AGENT: Nice to meet you, John. And what's your date of birth?

USER:  March 15th, 1985.

AGENT: Got it - March 15th, 1985. What's the best phone number to 
       reach you?

USER:  555-123-4567.

AGENT: Perfect. Now, what brings you in to the clinic today?

USER:  I've been having really bad headaches for the past few days. 
       They're mostly in the front of my head and I feel nauseous too.

AGENT: I'm sorry to hear that. How long have you been experiencing 
       these headaches?

USER:  About three days now.

AGENT: And on a scale of 1 to 10, with 10 being the worst, how would 
       you rate the pain?

USER:  I'd say about a 7.

AGENT: Thank you. Do you have any chronic medical conditions, like 
       diabetes or high blood pressure?

USER:  Yes, I have high blood pressure.

AGENT: Noted. Any past surgeries?

USER:  I had my appendix removed back in 2010.

AGENT: Got it. Are you currently taking any medications?

USER:  Yes, I take lisinopril for my blood pressure. 10 milligrams 
       every morning.

AGENT: Lisinopril, 10 milligrams daily. Now, this is important - 
       do you have any drug allergies?

USER:  Yes, I'm allergic to penicillin.

AGENT: What kind of reaction do you have to penicillin?

USER:  I get a rash and some swelling.

AGENT: Thank you for letting me know. Any food allergies?

USER:  No, no food allergies.

AGENT: Okay. Let me confirm what I have. Your name is John Smith, 
       date of birth March 15th, 1985. You're coming in for severe 
       headaches that you've had for 3 days, rated 7 out of 10, 
       with nausea. You have high blood pressure and take lisinopril 
       10 milligrams daily. You had an appendectomy in 2010. 
       And importantly, you're allergic to penicillin which causes 
       rash and swelling. No food allergies. Does all of that 
       sound correct?

USER:  Yes, that's all correct.

AGENT: Excellent! Your intake is complete. The clinical team will 
       have your information ready. Please check in at the front 
       desk when you arrive. Thank you, John, and I hope you 
       feel better soon!
```

### B. API Endpoints (Draft)

```
POST /api/session/start
  → Creates new intake session
  → Returns: { session_id, daily_room_url, token }

GET /api/session/{session_id}/status
  → Returns current state and collected data

POST /api/session/{session_id}/end
  → Ends session, returns final data

GET /api/session/{session_id}/transcript
  → Returns full conversation transcript

GET /api/session/{session_id}/summary
  → Returns human-readable summary
```

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | Hamza Khaled | Initial MVP PRD |

---

*End of Document*