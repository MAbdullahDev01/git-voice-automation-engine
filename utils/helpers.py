import re
import json
from subprocess import run, CalledProcessError

from core.jarvis import send_to_jarvis

def run_command(command : list[str]) -> str:

    try:
        result = run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False
        )
    except CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

    if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"
        
    return result.stdout.strip()

def get_context(user_input, stage, diff,):
    return send_to_jarvis(f"Git status:\n{stage}\n\nGit diff:\n{diff}\n\nUser input:\n{user_input}\n\nPlease provide a commit message based on the above context.")

def parse_llm_json(raw_response: str) -> dict:
    """Safely extracts and parses JSON from an LLM response string."""
    if not raw_response or not raw_response.strip():
        return {}

    # 1. Clean markdown code blocks if the LLM wrapped its JSON output
    cleaned = re.sub(r"```(?:json)?\s*", "", raw_response, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    # 2. Extract JSON object substring if extra text precedes/follows it
    json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(0)

    # 3. Parse JSON safely
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON Parsing Error: {e}")
        print(f"Raw Output was: {raw_response}")
        return {}