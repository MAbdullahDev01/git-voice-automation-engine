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
    return send_to_jarvis(
        f"Git status:\n{stage}\n\nGit diff:\n{diff}\n\nUser input:\n{user_input}\n\nPlease provide a commit message based on the above context.",
        stream=False,
    )

def clean_commit_message(raw_response: str) -> str:
    if not raw_response or not raw_response.strip():
        return ""

    cleaned = re.sub(r"```(?:text|md|markdown)?\s*", "", raw_response, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()

    lines = [line.rstrip() for line in cleaned.splitlines()]
    non_empty_lines = [line for line in lines if line.strip()]

    if not non_empty_lines:
        return ""

    subject = non_empty_lines[0].strip()
    body_lines = non_empty_lines[1:]

    if not body_lines:
        return subject

    body = " ".join(body_lines).strip()
    body_words = body.split()
    if len(body_words) > 100:
        body = " ".join(body_words[:100]).rstrip() + "..."

    return f"{subject}\n\n{body}" if body else subject

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
        print(f"JSON Parsing Error: {e}")
        print(f"Raw Output was: {raw_response}")
        return {}

def looks_ambiguous(text: str) -> bool:
    pronoun_pattern = re.compile(r"\b(it|that|this|him|her|them|again)\b", re.I)
    return bool(pronoun_pattern.search(text))