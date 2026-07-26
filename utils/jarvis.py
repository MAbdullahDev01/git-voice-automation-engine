import requests as r

from config import OLLAMA_URL, MODEL_NAME

def send_to_jarvis(user_message: str) -> str:
    if not OLLAMA_URL or not MODEL_NAME:
        return "Error: Ollama configuration is missing. Check OLLAMA_URL and MODEL_NAME."

    payload: dict = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": user_message}],
        "stream": False
    }

    try:
        print("Jarvis is thinking...")
        response = r.post(url=OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except r.exceptions.RequestException:
        return "Error: Cannot connect to Ollama. Make sure the application is running in your system tray."