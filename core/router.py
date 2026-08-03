from core.schemas import CommandPayload
from utils.groq import call_groq
from utils.helpers import parse_llm_json

ROUTER_SYSTEM_PROMPT = """
You are the central Command Router for JARVIS, an AI co-pilot.
Your job is to analyze raw, non-professional user speech or text inputs, classify the exact INTENT, and generate an refined QUERY string.

AVAILABLE INTENTS:
1. "git_create_branch": User wants to create a new git branch.
   - query value: name of the new branch.
2. "git_switch_branch": User wants to switch to an existing git branch.
   - query value: name of the branch to switch to.
3. "git_delete_branch": User wants to delete an existing git branch.
   - query value: name of the branch to delete.
4. "git_commit": User wants to commit code changes.
   - query value: summary of request or empty string (git tool will handle diff extraction).
5. "git_list_branches": User wants to list all git branches.
   - query value: (no value needed)
6. "git_current_branch": User wants to know the current git branch.
   - query value: (no value needed)
7. "spotify_play": User wants to listen to music.
   - QUERY RULE: Extract ONLY the raw song title and artist name. Remove action words like 'play', 'put on', 'listen to', single quotes, or extra symbols.
   - Expand common abbreviations (e.g., 'thenbhd' -> 'The Neighbourhood').
   - Example: "play reflections by thenbhd" -> Query: "Reflections The Neighbourhood"
8. "spotify_pause": User wants to pause the currently playing music.
   - query value: (no value needed)
9. "spotify_skip": User wants to skip to the next track.
   - query value: (no value needed)
10. "spotify_previous": User wants to go back to the previous track.
   - query value: (no value needed)
11. "general_chat": Any conversational query, technical question, or coding help.
   - IMPORTANT FOR QUERY: Transform the user's raw/vague input into a highly concise, professional, clear, and context-rich prompt ready for a technical assistant.

OUTPUT FORMAT:
You MUST reply strictly in valid JSON matching this schema:
{
   "intent": "<intent_name>",
   "query": "<extracted_target_or_expanded_prompt>"
}
"""

def route_command(user_input: str, context : str = "") -> dict:
   """Classifies user input and returns a dictionary with 'intent' and 'query'."""
   prompt = f"User Input: {user_input}"
   if context:
      prompt += f"\nContext: {context}"
   raw_response = call_groq(ROUTER_SYSTEM_PROMPT, prompt, json_mode=True, smart_model=False)
   payload = parse_llm_json(raw_response)

   try:
      # Validate dictionary against Pydantic schema
      validated_payload = CommandPayload.model_validate(payload)
      return validated_payload.model_dump()
      
   except Exception as e:
      print(f"Router Parsing Error: {e}. Falling back to general chat.")
      return {
         "intent": "general_chat", 
         "query": user_input
      }