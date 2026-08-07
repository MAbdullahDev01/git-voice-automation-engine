import re
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

def looks_ambiguous(text: str) -> bool:
    pronoun_pattern = re.compile(r"\b(it|that|this|him|her|them|again)\b", re.I)
    return bool(pronoun_pattern.search(text))