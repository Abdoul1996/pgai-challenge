# Architecture

## Big Picture 
Patient Scenario
        │
        ▼
Python Orchestrator
        │
        ▼
Vapi
        │
        ▼
Athena (Pretty Good AI)
        │
        ▼
Webhook
        │
        ▼
Transcript + Recording + Metadata
        │
        ▼
Evaluation Report

A Python orchestrator reads patient personas from `scenarios/personas.json` and fires outbound calls through Vapi's REST API. Each call runs GPT-4o (via Vapi) as the patient brain, ElevenLabs for voice synthesis, and Deepgram for transcription. Calls dial Pretty Good AI's test number (+1-805-439-8008), where their AI receptionist, Athena, answers. When a call ends, Vapi posts an end-of-call webhook to a local FastAPI server (exposed via ngrok), which downloads the recording and writes the transcript and metadata to disk for review.

I built on Vapi rather than wiring telephony, an LLM, TTS, and STT together by hand so the time went into test design instead of infrastructure plumbing. Capture is webhook-driven rather than polled, which keeps results real-time and avoids burning API calls on status checks. Calls run sequentially with a 4-minute gap so each one fully completes before the next begins — this sidesteps race conditions on the shared receptionist and keeps failures easy to isolate and debug. Every persona dials the same test number per Kevin's challenge spec; this means concurrent or back-to-back state on Athena's side could bleed across calls, so it's documented here as a known confound rather than treated as controlled.

| Decision                           | Benefit                                               | Trade-off                                                  |
| ---------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------- |
| Vapi instead of building telephony | Faster development and less infrastructure complexity | Less control over the underlying voice pipeline            |
| JSON-based scenarios               | Easy to extend and maintain                           | Complex scenarios require more verbose prompts             |
| Sequential execution               | Deterministic and easier to debug                     | Longer total runtime                                       |
| Webhooks instead of polling        | Efficient, event-driven processing                    | Requires local webhook exposure (ngrok) during development |

