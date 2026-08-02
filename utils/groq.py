from groq import Groq
from config import GROQ_API_KEY, GROQ_FAST_MODEL, GROQ_SMART_MODEL

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is missing or empty.")

if not GROQ_FAST_MODEL:
    raise ValueError("GROQ_FAST_MODEL is not defined in config.")

if not GROQ_SMART_MODEL:
    raise ValueError("GROQ_SMART_MODEL is not defined in config.")

# Initialize Groq client instance
client = Groq(api_key=GROQ_API_KEY)


def call_groq(
    system_prompt: str,
    user_input: str,
    json_mode: bool = False,
    smart_model: bool = False
) -> str:
    """Wrapper for calling Groq API using either fast (8B) or smart (70B) inference models."""
    try:
        # Groq's json_object mode requires the word 'JSON' in the system prompt
        if json_mode and "json" not in system_prompt.lower():
            system_prompt += "\nRespond strictly in valid JSON format."

        response_format = {"type": "json_object"} if json_mode else {"type": "text"}
        selected_model = GROQ_SMART_MODEL if smart_model else GROQ_FAST_MODEL

        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1 if json_mode else 0.7,  # Deterministic for intent routing
            response_format=response_format
        )
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq API Error: {e}")
        return ""