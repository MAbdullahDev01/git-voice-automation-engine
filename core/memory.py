# TODO: Consider adding a more advanced memory system that can summarize or prioritize important information over time, rather than just keeping the last N turns. This could involve natural language processing techniques to identify key points in the conversation.

class SimpleMemory:
    def __init__(self, max_turns: int = 5):
        """
        max_turns: Number of recent user-assistant interactions to keep.
        """
        self.max_turns = max_turns
        self.history : list[dict] = []  # i.e [{"role": "user/assistant", "content": "..."}]

    def add_message(self, role: str, content: str):
        """Appends a new message and trims oldest entries if limit exceeded."""
        self.history.append({"role": role, "content": content})
        
        # Keep only the last (max_turns * 2) messages (each turn = 1 user + 1 assistant)
        max_messages = self.max_turns * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]

    def get_context_prompt(self) -> str:
        """Formats stored history for injection into prompt context."""
        if not self.history:
            return ""

        formatted_turns = []
        for msg in self.history:
            prefix = "User" if msg["role"] == "user" else "JARVIS"
            formatted_turns.append(f"{prefix}: {msg['content']}")

        return "Recent Conversation History:\n" + "\n".join(formatted_turns)

    def clear(self):
        """Resets short-term memory session."""
        self.history = []