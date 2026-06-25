"""Thin wrapper around the Vapi API: place outbound calls."""

import json
import logging
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Step 1: Load Secrets from .env 

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")

if not VAPI_API_KEY:
    raise RuntimeError("VAPI_API_KEY is not set. Add it to your .env file.")
if not VAPI_PHONE_NUMBER_ID:
    raise RuntimeError("VAPI_PHONE_NUMBER_ID is not set. Add it to your .env file.")

VAPI_CALL_URL = "https://api.vapi.ai/call"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Step 2 : Define Function 

def create_outbound_call(
    to_number: str,
    system_prompt: str,
    first_message: str,
    assistant_name: str = "Patient Bot",
) -> dict:
    """Create an outbound Vapi call and return the parsed JSON response.

    Args:
        to_number: E.164-formatted phone number to call (e.g., "+18054398008").
        system_prompt: System message that defines the assistant's persona/behavior.
        first_message: The first thing the assistant says when the call connects.
        assistant_name: Display name for the assistant.

    Returns:
        Parsed JSON response from the Vapi API.
    """
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {"number": to_number},
        "assistant": {
            "name": assistant_name,
            "firstMessage": first_message,
            "model": {
                "provider": "openai",
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt},
                ],
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM",
            },
            "transcriber": {
                "provider": "deepgram",
                "model": "nova-2",
                "language": "en",
            },
        },
    }

    # Step 3 & 4:  Build the request and Send to VAPI to via HTTP 

    response = requests.post(VAPI_CALL_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    logger.info("Created Vapi call id=%s status=%s", data.get("id"), data.get("status"))
    return data


if __name__ == "__main__":
    # Resolve personas.json relative to the project root, not the src/ folder.
    PROJECT_ROOT = Path(__file__).parent.parent
    PERSONAS_PATH = PROJECT_ROOT / "scenarios" / "personas.json"

    with open(PERSONAS_PATH) as f:
        personas = json.load(f)

    available_ids = [p["id"] for p in personas]

    if len(sys.argv) < 2:
        print("Usage: python src/vapi_client.py <persona_id>")
        print(f"Available persona IDs: {', '.join(available_ids)}")
        sys.exit(1)

    persona_id = sys.argv[1]
    persona = next((p for p in personas if p["id"] == persona_id), None)

    if persona is None:
        print(f"Error: persona '{persona_id}' not found.")
        print(f"Available persona IDs: {', '.join(available_ids)}")
        sys.exit(1)

    result = create_outbound_call(
        to_number=os.getenv("PGAI_TEST_NUMBER"),
        system_prompt=persona["system_prompt"],
        first_message=persona["first_message"],
        assistant_name=persona["name"],
    )

    print(
        f"Placed call for persona {persona['id']} ({persona['name']}): "
        f"call_id={result.get('id')}"
    )
