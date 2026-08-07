from core.schemas import CommandPayload
from utils.groq import call_groq_structured

ROUTER_SYSTEM_PROMPT = """
You are the central Command Router for JARVIS, an AI co-pilot.
Your job is to analyze user speech/text (plus any injected conversation context), classify the exact INTENT, and generate a refined QUERY string.

AVAILABLE INTENTS:
1. "git_create_branch": User wants to create a new git branch.
   - query: name of the new branch.
2. "git_switch_branch": User wants to switch to an existing git branch.
   - query: name of the branch to switch to.
3. "git_delete_branch": User wants to delete an existing git branch.
   - query: name of the branch to delete.
4. "git_commit": User wants to commit code changes.
   - query: summary of commit request or empty string.
5. "git_list_branches": User wants to list all git branches.
   - query: ""
6. "git_current_branch": User wants to know the current active git branch.
   - query: ""

7. "spotify_play": User EXPLICITLY commands music to play, start, or resume (e.g., "play...", "put on...", "listen to...").
   - QUERY RULE: Extract ONLY the raw song title and artist name. Remove action words ("play", "put on"), quotes, or extra symbols.
   - Expand common abbreviations (e.g., 'thenbhd' -> 'The Neighbourhood').
   - Example: "play reflections by thenbhd" -> Query: "Reflections The Neighbourhood"
   - AUTO-CORRECT SPELLING/STT: Only correct spelling if you are highly confident of the exact song and artist. If the title sounds non-English/transliterated and you are not certain of the exact official spelling, return the user's original phrasing unchanged rather than guessing.
   Examples:
      - "rakhlo tum chapke" -> "Rakhlo Tum Chupake"
      - "arbit bala" -> "Arpit Bala"
      - "reflections by thenbhd" -> "Reflections The Neighbourhood"

8. "spotify_pause": User wants to pause or stop music playback.
   - query: ""
9. "spotify_skip": User wants to skip to the next track.
   - query: ""
10. "spotify_previous": User wants to go back to the previous track.
   - query: ""
11. "spotify_info": User asks for information about the currently playing music, artist, or album (e.g., "what song is this?", "who sings this?").
   - query: "current_track_info"

12. "general_chat": Conversational input, technical/coding help, general questions, or PASSIVE STATEMENTS (e.g., "this artist is good", "i love this track").
   - QUERY RULE: Transform raw input into a concise, context-rich prompt for an AI assistant.

CRITICAL ROUTING & MEMORY RULES:
- RULE 1 (PASSIVE VS COMMAND): Opinions or statements like "arbit bala is so good" MUST be classified as "general_chat", NOT "spotify_play".
- RULE 2 (STRICT CONTEXT USE): Use conversation history ONLY to resolve ambiguous pronouns ("play it again", "who sings that?"). 
- RULE 3 (NO QUERY ISOLATION LEAKAGE): NEVER combine keywords from past conversation history with a NEW explicit play request unless the user explicitly orders a mashup. (e.g., If history mentions "Arbit Bala" and user says "play reflections", query MUST be "Reflections", NOT "Reflections Arbit Bala").

OUTPUT FORMAT:
Reply strictly in valid JSON:
{
    "intent": "<intent_name>",
    "query": "<extracted_target_or_expanded_prompt>"
}

DISAMBIGUATION EXAMPLES (question/opinion vs command):

Input: "should I create a branch for this feature?"
-> {"intent": "general_chat", "query": "Advice on whether to create a branch for this feature", "confidence": 0.9}

Input: "create a branch called feature/login"
-> {"intent": "git_create_branch", "query": "feature/login", "confidence": 0.97}

Input: "what happens if I delete the main branch?"
-> {"intent": "general_chat", "query": "Explain the consequences of deleting the main branch", "confidence": 0.9}

Input: "delete the branch called old-login"
-> {"intent": "git_delete_branch", "query": "old-login", "confidence": 0.96}

Input: "this song is so good"
-> {"intent": "general_chat", "query": "User is expressing enjoyment of the currently playing song", "confidence": 0.9}

Input: "play something like this"
-> {"intent": "spotify_play", "query": "something like this", "confidence": 0.7}

RULE: If the input is a question, opinion, or statement ABOUT an action rather than
a direct instruction to perform it, classify as general_chat. If uncertain, lower confidence
and prefer general_chat.
"""

COMMAND_SCHEMA = {
   "type": "object",
   "properties": {
      "intent": {"type": "string", "enum": [
            "git_commit", "git_create_branch", "git_switch_branch",
            "git_delete_branch", "git_list_branches", "git_current_branch",
            "spotify_play", "spotify_pause", "spotify_skip",
            "spotify_previous", "spotify_info", "general_chat",
      ]},
      "query": {"type": "string"},
      "confidence": {"type": "number"},
   },
   "required": ["intent", "query", "confidence"],
   "additionalProperties": False,
}

CONFIDENCE_THRESHOLD = 0.6

def route_command(user_input: str, context: str = "") -> dict:
   prompt = f"User Input: {user_input}" + (f"\nContext: {context}" if context else "")
   try:
      payload = call_groq_structured(ROUTER_SYSTEM_PROMPT, prompt, COMMAND_SCHEMA, smart_model=True)
      validated = CommandPayload.model_validate(payload)
      if validated.confidence < CONFIDENCE_THRESHOLD and validated.intent != "general_chat":
         return {"intent": "general_chat", "query": user_input, "confidence": validated.confidence}
      return validated.model_dump()
   except Exception as e:
      print(f"Router error: {e}. Falling back to general chat.")
      return {"intent": "general_chat", "query": user_input, "confidence": 0.0}