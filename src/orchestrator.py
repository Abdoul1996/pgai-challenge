"""Main entry point. Loops through patient personas and triggers calls via Vapi."""

import argparse
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from vapi_client import create_outbound_call

PROJECT_ROOT = Path(__file__).parent.parent
PERSONAS_PATH = PROJECT_ROOT / "scenarios" / "personas.json"

CALL_GAP_SECONDS = 240  # wait for each call to complete before the next


def load_personas() -> list[dict]:
    """Load all personas from scenarios/personas.json."""
    with open(PERSONAS_PATH) as f:
        return json.load(f)


def select_personas(personas: list[dict], args: argparse.Namespace) -> list[dict]:
    """Filter personas based on CLI args; default is all personas."""
    by_id = {p["id"]: p for p in personas}

    if args.persona_id:
        return [by_id[args.persona_id]]
    if args.personas:
        ids = [pid.strip() for pid in args.personas.split(",") if pid.strip()]
        return [by_id[pid] for pid in ids]
    return personas


def run(personas: list[dict], to_number: str) -> dict[str, str]:
    """Fire a call for each persona; return a persona_id -> call_id map."""
    total = len(personas)
    results: dict[str, str] = {}

    for i, persona in enumerate(personas, start=1):
        print(f"[{i}/{total}] Firing persona {persona['id']} ({persona['name']})...")
        response = create_outbound_call(
            to_number=to_number,
            system_prompt=persona["system_prompt"],
            first_message=persona["first_message"],
            assistant_name=persona["name"],
        )
        call_id = response.get("id")
        results[persona["id"]] = call_id
        print(f"  → call_id={call_id}")

        if i < total:
            time.sleep(CALL_GAP_SECONDS)

    return results


def print_summary(results: dict[str, str]) -> None:
    """Print a persona_id -> call_id summary table."""
    print("\n=== Summary ===")
    print(f"{'persona_id':<20} call_id")
    print(f"{'-' * 20} {'-' * 36}")
    for persona_id, call_id in results.items():
        print(f"{persona_id:<20} {call_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fire Vapi calls for patient personas.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--persona-id", help="Run a single persona by id.")
    group.add_argument("--personas", help="Run a comma-separated subset of persona ids.")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    to_number = os.getenv("PGAI_TEST_NUMBER")

    args = parse_args()
    personas = select_personas(load_personas(), args)
    results = run(personas, to_number)
    print_summary(results)


if __name__ == "__main__":
    main()
