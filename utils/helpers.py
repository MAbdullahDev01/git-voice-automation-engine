import re
from subprocess import run, CalledProcessError

from utils.jarvis import send_to_jarvis

def clean_commit_message(raw_output: str) -> str:
    """Extracts just the commit message string regardless of LLM formatting."""
    # 1. Look for content inside quotes after -m (e.g., git commit -m "feat: my change")
    match = re.search(r'git commit -m\s*["\']([^"\']+)["\']', raw_output)
    if match:
        return match.group(1).strip()
    
    # 2. Look for any line starting with conventional types (feat:, fix:, chore:, etc.)
    match = re.search(r'^(feat|fix|chore|docs|style|refactor)(\(.*\))?:\s*.+$', raw_output, re.MULTILINE)
    if match:
        return match.group(0).strip()
    
    # 3. Fallback: Strip git commands, quotes, and backticks line by line
    clean_lines = []
    for line in raw_output.splitlines():
        line = line.strip()
        if not line or line.startswith("git add") or line.startswith("```"):
            continue
        line = re.sub(r'^git commit -m\s*', '', line)
        line = line.strip('"\'` ')
        if line:
            clean_lines.append(line)
            
    return clean_lines[0] if clean_lines else "chore: update codebase"

def run_command(command : list[str]) -> str:

    try:
        result = run(command, capture_output=True, text=True, check=True)
    except CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"

    return result.stdout

def get_context(user_input, stage, diff,):
    return send_to_jarvis(f"Git status:\n{stage}\n\nGit diff:\n{diff}\n\nUser input:\n{user_input}\n\nPlease provide a commit message based on the above context.")