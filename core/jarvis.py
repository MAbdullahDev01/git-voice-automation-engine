from utils.groq import call_groq

SYSTEM_PROMPT = """
You are Jarvis, a helpful, friendly, and highly intelligent AI assistant. 
Answer the user's questions clearly, concisely, and accurately.
"""

def send_to_jarvis(user_message: str, stream: bool = True):
    return call_groq(
        system_prompt=SYSTEM_PROMPT, 
        user_input=user_message, 
        json_mode=False, 
        smart_model=True,
        stream=stream
    )