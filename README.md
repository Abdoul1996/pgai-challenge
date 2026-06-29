# Pretty Good AI — Engineering Challenge

An automated voice bot that stress-tests Pretty Good AI's AI receptionist, **Athena**. It places outbound phone calls driven by simulated patient personas (scheduling, refills, insurance questions, and edge cases like refusing a DOB or interrupting mid-sentence), captures the recording and transcript for each call, and surfaces the bugs that show up along the way. Personas live in `scenarios/personas.json`; calls are placed through Vapi, and end-of-call webhooks save each recording, transcript, and metadata bundle to `calls/`.

## Setup

**Prerequisites:** Python 3.11+, [ngrok](https://ngrok.com/), a [Vapi](https://vapi.ai/) account, and OpenAI access (used via Vapi).

Clone and enter the project:

```bash
git clone https://github.com/Abdoul1996/pgai-challenge.git
cd pgai-challenge
```

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Configure environment variables:

```bash
cp .env.example .env
# Edit .env and fill in VAPI_API_KEY, VAPI_PHONE_NUMBER_ID, OPENAI_API_KEY, etc.
```

Start the webhook server in one terminal:

```bash
python src/webhook_server.py
```

Expose it with ngrok in a second terminal:

```bash
ngrok http 8000
```

Copy the ngrok HTTPS URL, then paste it into the Vapi dashboard under **Phone Numbers → Server URL**, appending the webhook path:

```
https://<your-ngrok-subdomain>.ngrok-free.dev/vapi-webhook
```

> ⚠️ ngrok issues a new URL each time it restarts — re-copy it into the Vapi dashboard whenever you restart ngrok.

## Running calls

Single persona:

```bash
python src/vapi_client.py p01_maria_baseline
```

All personas as a sequential batch (4-minute gap between calls):

```bash
cd src && python orchestrator.py
```

A subset of personas:

```bash
python orchestrator.py --personas p01_maria_baseline,p06_refuses_dob,p09_interrupter
```

## Deliverables

- **10 captured calls** — recordings, transcripts, and metadata in `calls/`
- **Bug report** — `BUG_REPORT.md`
- **Architecture notes** — `ARCHITECTURE.md`
- **Loom walkthrough** — [https://www.loom.com/share/cb0623702b92449ab7472d964628a8ef]


## Project structure

```
pgai-challenge/
├── src/
│   ├── vapi_client.py      # Places a single outbound call (CLI: <persona_id>)
│   ├── orchestrator.py     # Batches calls across personas
│   ├── webhook_server.py   # FastAPI server; saves recording/transcript/metadata
│   └── ...
├── scenarios/
│   └── personas.json       # 10 patient personas
└── calls/
    ├── call_001/           # recording.mp3, transcript.txt, metadata.json
    ├── call_002/
    └── ...
```

## Cost note

The full run of 10 calls used roughly **~$3** of Vapi credit total.
