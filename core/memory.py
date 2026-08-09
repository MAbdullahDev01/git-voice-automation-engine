# Imports
import json
from pathlib import Path
from utils.groq import call_groq

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
            print(f"Memory load failed ({e}), starting fresh.")

    def _save(self):
        try:
            self.filepath.write_text(
                json.dumps({"history": self.history, "summary": self.summary}, indent=2),
                encoding="utf-8",
            )
        except OSError as e:
            print(f"Memory save failed: {e}")

    # ---------- summarization ---------- #

    def _summarize_overflow(self, overflow: list[dict]):
            overflow_text = "\n".join(f"{m['role']}: {m['content']}" for m in overflow)
            prompt = f"Existing summary:\n{self.summary}\n\nNew turns to fold in:\n{overflow_text}\n\nProduce a single updated, concise summary (2-4 sentences)."
            try:
                self.summary = call_groq(
                    system_prompt="You compress conversation history into brief factual summaries.",
                    user_input=prompt,
                    json_mode=False,
                    smart_model=True,
                    stream=False,
                )
            except Exception:
                pass

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