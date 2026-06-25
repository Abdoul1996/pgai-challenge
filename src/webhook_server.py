"""Webhook server that receives Vapi call events (status updates, end-of-call reports, recording URLs)."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Body, FastAPI

load_dotenv()

CALLS_DIR = Path(__file__).resolve().parent.parent / "calls"
CALL_FOLDER_RE = re.compile(r"^call_(\d{3})$")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()


def next_call_folder() -> Path:
    """Return calls/call_NNN/ with NNN one higher than the highest existing folder."""
    CALLS_DIR.mkdir(parents=True, exist_ok=True)
    existing = []
    for entry in CALLS_DIR.iterdir():
        if entry.is_dir():
            match = CALL_FOLDER_RE.match(entry.name)
            if match:
                existing.append(int(match.group(1)))
    next_n = (max(existing) + 1) if existing else 1
    folder = CALLS_DIR / f"call_{next_n:03d}"
    folder.mkdir(parents=True, exist_ok=False)
    return folder


def download_recording(url: str, dest: Path) -> bool:
    """Stream a recording to disk. Return True on success, False on failure."""
    try:
        with requests.get(url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with dest.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except requests.RequestException as exc:
        logger.error("Failed to download recording from %s: %s", url, exc)
        return False


@app.post("/vapi-webhook")
def vapi_webhook(payload: dict = Body(...)) -> dict:
    """Receive Vapi webhooks and persist end-of-call artifacts to disk."""
    message: dict[str, Any] = payload.get("message", {})
    message_type = message.get("type")
    logger.info("Webhook received: type=%s", message_type)

    # Always save the raw payload to a temp file so we can inspect
    # exactly what Vapi sent us during development
    debug_dir = CALLS_DIR / "_webhook_debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    debug_file = debug_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_{message_type}.json"
    debug_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Raw payload saved to %s", debug_file)

    if message_type != "end-of-call-report":
        logger.info("Ignoring webhook of type=%s", message_type)
        return {"status": "ignored", "type": message_type}

    call = message.get("call", {}) or {}
    call_id = call.get("id")
    recording_url = message.get("recordingUrl")
    transcript = message.get("transcript", "") or ""
    summary = message.get("summary", "") or ""
    ended_reason = message.get("endedReason")
    duration_seconds = message.get("durationSeconds")
    cost = message.get("cost")

    folder = next_call_folder()

    if recording_url:
        download_recording(recording_url, folder / "recording.mp3")
    else:
        logger.warning("No recordingUrl present for call_id=%s", call_id)

    (folder / "transcript.txt").write_text(transcript, encoding="utf-8")

    metadata = {
        "call_id": call_id,
        "ended_reason": ended_reason,
        "duration_seconds": duration_seconds,
        "cost": cost,
        "summary": summary,
        "recording_url": recording_url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "folder_name": folder.name,
    }
    (folder / "metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    logger.info(
        "Saved %s: %s, duration=%ss, cost=$%s",
        folder.name,
        call_id,
        duration_seconds,
        cost,
    )
    return {"status": "saved", "folder": folder.name, "call_id": call_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
