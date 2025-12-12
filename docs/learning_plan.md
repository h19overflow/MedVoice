# MedVoice Study Guide

A structured learning path for building a real-time voice AI patient intake agent. Study in order — each section builds on the previous.

---

## 1. Voice Activity Detection (VAD)

**What you're learning:** Detecting when a user starts/stops speaking to trigger STT.

| Topic | Resource |
|-------|----------|
| Silero VAD Overview | https://github.com/snakers4/silero-vad |
| Silero VAD PyTorch Hub | https://pytorch.org/hub/snakers4_silero-vad_vad/ |
| Pipecat's Silero Integration | https://docs.pipecat.ai/server/utilities/audio/silero-vad-analyzer |

**Key concepts to understand:**
- Speech probability threshold (0-1 confidence score)
- `min_speech_duration` — avoid triggering on noise
- `min_silence_duration` — when to consider speech "ended"
- Sample rates: 8kHz vs 16kHz
- Ring buffer for pre-roll audio (capture speech start)

---

## 2. Speech-to-Text (STT)

**What you're learning:** Converting audio streams to text in real-time.

| Topic | Resource |
|-------|----------|
| Deepgram Documentation Home | https://developers.deepgram.com/docs/introduction |
| Deepgram STT Getting Started | https://developers.deepgram.com/docs/stt/getting-started |
| Deepgram Python SDK | https://github.com/deepgram/deepgram-python-sdk |
| Streaming STT (WebSocket) | https://developers.deepgram.com/docs/streaming-overview |
| Nova-2 vs Flux Models | https://developers.deepgram.com/docs/models-overview |

**Key concepts to understand:**
- Streaming vs batch transcription
- WebSocket connection lifecycle
- Interim vs final transcripts
- Model selection: Nova-2 (accuracy) vs Flux (conversational, turn detection)
- Encoding formats: linear16, mulaw
- Sample rate matching (16000 Hz recommended)

---

## 3. Text-to-Speech (TTS)

**What you're learning:** Converting agent responses to natural-sounding speech.

| Topic | Resource |
|-------|----------|
| Deepgram TTS Getting Started | https://developers.deepgram.com/docs/text-to-speech |
| Deepgram TTS Streaming (WebSocket) | https://developers.deepgram.com/docs/tts-websocket |
| Voice Selection (Aura voices) | https://developers.deepgram.com/docs/tts-models |
| Audio Format Options | https://developers.deepgram.com/docs/tts-media-output-settings |

**Key concepts to understand:**
- Streaming TTS for low latency (don't wait for full response)
- Voice model selection (Aura-2 voices)
- Audio encoding: linear16, mp3, opus
- TTFB (Time to First Byte) optimization
- Chunked audio delivery

---

## 4. WebRTC Fundamentals

**What you're learning:** Real-time audio/video transport between browser and server.

| Topic | Resource |
|-------|----------|
| WebRTC Overview | https://webrtc.org/ |
| MDN WebRTC Guide | https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API |
| Google WebRTC Codelab | https://codelabs.developers.google.com/codelabs/webrtc-web |
| WebRTC Audio Streams | https://www.videosdk.live/developer-hub/webrtc/webrtc-audio-stream |

**Key concepts to understand:**
- RTCPeerConnection — the core connection object
- MediaStream and MediaStreamTrack — audio/video data
- ICE candidates — network traversal
- STUN/TURN servers — NAT penetration
- Signaling — exchanging connection metadata
- Why WebRTC over WebSocket for voice (latency, jitter handling)

---

## 5. Daily.co Transport

**What you're learning:** Using Daily's WebRTC infrastructure for voice agents.

| Topic | Resource |
|-------|----------|
| Daily.co Documentation | https://docs.daily.co/ |
| Daily + Pipecat Guide | https://docs.daily.co/guides/products/ai-toolkit |
| Daily WebRTC in Pipecat | https://docs.pipecat.ai/deployment/pipecat-cloud/guides/daily-webrtc |
| Daily Bots Overview | https://www.daily.co/blog/daily-bots-build-real-time-voice-vision-and-video-ai-agents/ |

**Key concepts to understand:**
- Room creation and management
- Meeting tokens for authentication
- DailyTransport in Pipecat
- Free tier limits (10k minutes/month)
- When to use Daily vs SmallWebRTCTransport

---

## 6. Pipecat Framework (Core)

**What you're learning:** Orchestrating voice AI pipelines.

| Topic | Resource |
|-------|----------|
| Pipecat Introduction | https://docs.pipecat.ai/getting-started/introduction |
| Pipecat GitHub | https://github.com/pipecat-ai/pipecat |
| Quickstart Guide | https://docs.pipecat.ai/getting-started/quickstart |
| Pipeline Concepts | https://docs.pipecat.ai/guides/concepts/pipelines |
| Frame Processors | https://docs.pipecat.ai/guides/concepts/frames |

**Key concepts to understand:**
- Pipeline architecture: frames flow through processors
- Frame types: AudioRawFrame, TextFrame, TranscriptionFrame
- Processor chain: Transport → VAD → STT → LLM → TTS → Transport
- PipelineTask — runs your pipeline
- Context aggregators — manage conversation history
- Async processing with asyncio

---

## 7. Pipecat Services Integration

**What you're learning:** Connecting STT, TTS, and LLM services to Pipecat.

| Topic | Resource |
|-------|----------|
| Deepgram STT in Pipecat | https://docs.pipecat.ai/server/services/stt/deepgram |
| Deepgram TTS in Pipecat | https://docs.pipecat.ai/server/services/tts/deepgram |
| Google Gemini in Pipecat | https://docs.pipecat.ai/server/services/llm/google |
| Transport Options | https://docs.pipecat.ai/server/services/transport |

**Key concepts to understand:**
- Service initialization with API keys
- Service-specific parameters (model, voice, etc.)
- Streaming responses from LLM
- Error handling and retries

---

## 8. Pipecat Flows (Conversation State Machine)

**What you're learning:** Managing structured, multi-turn conversations.

| Topic | Resource |
|-------|----------|
| Pipecat Flows Guide | https://docs.pipecat.ai/guides/features/pipecat-flows |
| Pipecat Flows GitHub | https://github.com/pipecat-ai/pipecat-flows |
| Flows API Reference | https://reference-flows.pipecat.ai/ |
| Patient Intake Example | https://github.com/pipecat-ai/pipecat-flows/tree/main/examples |
| Visual Flow Editor | https://flows.pipecat.ai/ |

**Key concepts to understand:**
- NodeConfig — defines a conversation state
- role_messages vs task_messages
- Functions (tools) — trigger state transitions
- FlowManager — orchestrates the flow
- Context strategies: APPEND, RESET, RESET_WITH_SUMMARY
- Pre/post actions (tts_say, end_conversation)
- Dynamic flows vs static flows (use dynamic)

---

## 9. LLM Integration (Gemini)

**What you're learning:** Using Gemini for conversation and data extraction.

| Topic | Resource |
|-------|----------|
| Gemini API Documentation | https://ai.google.dev/gemini-api/docs |
| Gemini Models Overview | https://ai.google.dev/gemini-api/docs/models |
| Structured Output (JSON) | https://ai.google.dev/gemini-api/docs/structured-output |
| Function Calling | https://ai.google.dev/gemini-api/docs/function-calling |
| Python SDK | https://github.com/google/generative-ai-python |

**Key concepts to understand:**
- Model selection: gemini-2.5-flash (fast, cheap) vs gemini-2.5-pro
- Streaming responses for low latency
- Structured output with JSON schema
- Function calling for tool use
- System instructions for persona
- Temperature and safety settings

---

## 10. FastAPI Backend

**What you're learning:** Building the API server and WebSocket endpoints.

| Topic | Resource |
|-------|----------|
| FastAPI Documentation | https://fastapi.tiangolo.com/ |
| FastAPI WebSockets | https://fastapi.tiangolo.com/advanced/websockets/ |
| WebSocket Tutorial | https://betterstack.com/community/guides/scaling-python/fastapi-websockets/ |
| Pipecat FastAPI Transport | https://docs.pipecat.ai/server/services/transport/fastapi-websocket |

**Key concepts to understand:**
- Async endpoints with `async def`
- WebSocket lifecycle: accept, receive, send, close
- WebSocketDisconnect handling
- CORS configuration
- Dependency injection
- Pydantic models for request/response validation

---

## 11. React Frontend

**What you're learning:** Building the voice interface in React.

| Topic | Resource |
|-------|----------|
| Pipecat React SDK | https://docs.pipecat.ai/client/react/introduction |
| React Hooks Reference | https://docs.pipecat.ai/client/react/hooks |
| Pipecat JS Client | https://github.com/pipecat-ai/pipecat-client-web |
| Voice UI Kit | https://voiceuikit.pipecat.ai/ |
| Voice UI Kit GitHub | https://github.com/pipecat-ai/voice-ui-kit |

**Key concepts to understand:**
- PipecatClientProvider — context wrapper
- usePipecatClient — access client instance
- useRTVIClientEvent — subscribe to events
- PipecatClientAudio — automatic audio handling
- Transport state machine: idle → connecting → connected → disconnected
- VoiceVisualizer component

---

## 12. Pipecat Examples

**What you're learning:** Real-world patterns from working examples.

| Topic | Resource |
|-------|----------|
| Pipecat Examples Repository | https://github.com/pipecat-ai/pipecat-examples |
| Simple Chatbot | https://github.com/pipecat-ai/pipecat/tree/main/examples |
| Flows Examples | https://github.com/pipecat-ai/pipecat-flows/tree/main/examples |
| Patient Intake Flow | Look for `patient_intake` in flows examples |

---

## Study Order Recommendation

### Week 1: Foundation
1. **Day 1-2:** WebRTC fundamentals (MDN guide + Google codelab)
2. **Day 3:** Pipecat introduction + pipeline concepts
3. **Day 4:** Deepgram STT/TTS documentation
4. **Day 5:** Silero VAD basics
5. **Day 6-7:** Build a basic Pipecat "hello world" — echo bot

### Week 2: Integration
1. **Day 8-9:** Pipecat Flows documentation + patient intake example
2. **Day 10:** Gemini API — structured output + function calling
3. **Day 11:** FastAPI WebSockets
4. **Day 12:** Pipecat React SDK + Voice UI Kit
5. **Day 13-14:** Build the full intake flow

---

## Quick Reference Commands

```bash
# Install Pipecat with all services
pip install "pipecat-ai[daily,deepgram,google,silero]"

# Install Pipecat Flows
pip install pipecat-ai-flows

# Install React SDK
npm install @pipecat-ai/client-js @pipecat-ai/client-react @pipecat-ai/daily-transport

# Install Voice UI Kit
npm install @pipecat-ai/voice-ui-kit
```

---

## Environment Variables You'll Need

```bash
DEEPGRAM_API_KEY=your_key      # STT + TTS
GOOGLE_API_KEY=your_key        # Gemini LLM
DAILY_API_KEY=your_key         # WebRTC transport
```

---

## Tips

1. **Start with chat mode first** — Skip voice complexity, test your LLM logic
2. **Use Pipecat's examples** — Don't reinvent the wheel
3. **Read Pipecat Flows carefully** — It handles 80% of your state management
4. **Test with headphones** — Avoid echo feedback loops
5. **Check WebRTC internals** — `chrome://webrtc-internals` for debugging

---

*Good luck building MedVoice!*