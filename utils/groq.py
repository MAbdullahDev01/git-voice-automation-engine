from typing import Generator, Union
from groq import Groq
from config import GROQ_API_KEY, GROQ_FAST_MODEL, GROQ_SMART_MODEL

client = Groq(api_key=GROQ_API_KEY)

def call_groq(
    system_prompt: str, 
    user_input: str, 
    json_mode: bool = False, 
    smart_model: bool = False,
    stream: bool = True
) -> Union[str, Generator[str, None, None]]:
    
    selected_model = GROQ_SMART_MODEL if smart_model else GROQ_FAST_MODEL
    should_stream = stream and not json_mode

    kwargs = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.1 if json_mode else 0.7,
        "stream": should_stream,
    }

    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)

        if should_stream:
            def token_generator():
                for chunk in response:  # type: ignore
                    content = chunk.choices[0].delta.content or ""
                    if content:
                        yield content
            return token_generator()

        return response.choices[0].message.content.strip()  # type: ignore

    except Exception as e:
        print(f"Groq API Error: {e}")
        return "" if not should_stream else (chunk for chunk in [])