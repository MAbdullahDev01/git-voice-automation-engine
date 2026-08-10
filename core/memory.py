# Imports
import json
from pathlib import Path
from utils.groq import call_groq
from utils.logger import get_logger

# Logging
logger = get_logger(__name__)

# System prompt for summarization
SUMMARY_SYSTEM_PROMPT = """
You maintain a compact rolling memory summary for JARVIS, a desktop AI assistant.
You will be given the CURRENT SUMMARY (may be empty) and NEW CONVERSATION TURNS that
are about to be dropped from active memory. Merge them into one updated summary.

WHAT TO PRESERVE (in priority order):
1. Named entities exactly as stated: branch names, track/artist names, file paths,
project names, or anything a pronoun ("it", "that", "this") might later refer to.
2. Stated user preferences, facts, or corrections (e.g. "I meant the acoustic version",
"I prefer tabs over spaces").
3. Unresolved questions or open threads the user raised but didn't get closure on.
4. General topic/context of the conversation, in brief.

WHAT TO DROP:
- Pleasantries, filler, greetings.
- Tool execution results (commits, playback confirmations) — these are logged elsewhere
and do not belong in conversational memory.
- Anything already fully captured in the CURRENT SUMMARY — do not repeat, only add what's new.

RULES:
- Output ONLY the updated summary text. No preamble, no headers, no bullet points.
- Write in third person, past tense, factual — no speculation about intent or emotion.
- Keep it under 4 sentences. If the current summary is already near that limit, compress
it further rather than letting it grow — prioritize recency and specificity over completeness.
- Never invent details not present in the input.

EXAMPLES:

Current Summary: (empty)
New Turns:
User: create a branch called feature/audio-refactor
JARVIS: Created and switched to branch feature/audio-refactor.
User: play arbit bala
JARVIS: Playing Arpit Bala.
->
User created and switched to the branch feature/audio-refactor, and requested the track "Arpit Bala" to be played.

---

Current Summary: User created and switched to the branch feature/audio-refactor, and requested the track "Arpit Bala" to be played.
New Turns:
User: no I meant the slowed version, not the original
JARVIS: Noted, I'll look for the slowed version next time.
User: actually never mind, this is fine
->
User created and switched to the branch feature/audio-refactor. User initially wanted a slowed version of "Arpit Bala" instead of the original, then said the original was fine after all.

---

Current Summary: User is debugging a memory leak in the router module and mentioned it's been happening intermittently for a few days.
New Turns:
User: hey what's up
JARVIS: Not much, ready when you are.
User: can you remind me what model I should use for structured outputs on groq
JARVIS: openai/gpt-oss-120b and openai/gpt-oss-20b support structured outputs with strict mode on Groq.
->
User is debugging an intermittent memory leak in the router module (ongoing for a few days, unresolved). User was reminded that openai/gpt-oss-120b and openai/gpt-oss-20b support strict-mode structured outputs on Groq.

---

Current Summary: (empty)
New Turns:
User: commit my changes
JARVIS: Proposed Commit Message: "fix(router): add confidence gate". Do you want to proceed? (y/n)
User: y
JARVIS: Changes committed and pushed successfully.
->
(empty)
"""

# Create a directory for memory files if it doesn't exist
MEMORY_DIR = Path("data")
MEMORY_DIR.mkdir(exist_ok=True)

class SimpleMemory:
    def __init__(self, max_turns: int = 5, session_id: str = "default"):
        self.max_turns = max_turns
        self.session_id = session_id
        self.filepath = MEMORY_DIR / f"memory_{session_id}.json"
        self.history: list[dict] = []
        self.summary: str = ""
        self._load()

    # ---------- persistence ---------- #

    def _load(self):
        if not self.filepath.exists():
            return
        try:
            data = json.loads(self.filepath.read_text(encoding="utf-8"))
            self.history = data.get("history", [])
            self.summary = data.get("summary", "")
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Memory load failed ({e}), starting fresh.")

    def _save(self):
        try:
            self.filepath.write_text(
                json.dumps({"history": self.history, "summary": self.summary}, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            logger.error(f"Memory save failed: {e}")

    # ---------- summarization ---------- #

    def _summarize_overflow(self, overflow: list[dict]):
            overflow_text = "\n".join(f"{m['role']}: {m['content']}" for m in overflow)
            prompt = f"Existing summary:\n{self.summary}\n\nNew turns to fold in:\n{overflow_text}\n\nProduce a single updated, concise summary (2-4 sentences)."
            try:
                self.summary = call_groq(
                    system_prompt=SUMMARY_SYSTEM_PROMPT,
                    user_input=prompt,
                    json_mode=False,
                    smart_model=True,
                    stream=False,
                )
            except Exception as e:
                logger.error(f"Error summarizing memory overflow: {e}")

    # ---------- core API ----------

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            overflow = self.history[:len(self.history) - max_messages]
            self.history = self.history[-max_messages:]
            self._summarize_overflow(overflow)
        self._save()

    def get_context_prompt(self) -> str:
        parts = []
        if self.summary:
            parts.append(f"Summary of earlier conversation:\n{self.summary}")
        if self.history:
            formatted = [f"{'User' if m['role'] == 'user' else 'JARVIS'}: {m['content']}" for m in self.history]
            parts.append("Recent Conversation History:\n" + "\n".join(formatted))
        return "\n\n".join(parts)

    def clear(self):
        self.history = []
        self.summary = ""
        self._save()