"""Thin wrapper around the Vapi API: place outbound calls."""

import logging
import os

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
    test_number = os.getenv("PGAI_TEST_NUMBER")
    if not test_number:
        raise RuntimeError("PGAI_TEST_NUMBER is not set. Add it to your .env file.")

    create_outbound_call(
        to_number=test_number,
        system_prompt=(
            "You are Maria Rodriguez, 34 years old, calling Pivot Point Orthopedics "
            "to schedule an appointment for knee pain that has lasted 3 weeks. "
            "You're friendly but in a slight hurry because you're at work. "
            "Keep your responses short and natural, like a real phone call. "
            "If asked for your date of birth, say March 15, 1991. "
            "Don't break character — you ARE Maria, not an AI."
        ),
        first_message="Hi, I'd like to schedule an appointment with Dr. Patel.",
        assistant_name="Maria",
    )
