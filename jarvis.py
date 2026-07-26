import requests as r

from test_piper import speak_neral
from test_ears import listen_neural
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

if __name__ == "__main__":
    try:
        while True:
            user_input = input("You (type text or press Enter to talk): ").strip()
            
            if user_input.lower() == "quit":
                print("\nJarvis: Shutting down. Goodbye, sir!")
                speak_neral("Shutting down. Goodbye, sir!")
                break
                
            elif user_input == "":
                user_input = listen_neural()
                if not user_input:
                    continue
                print(f"You (Spoke): {user_input}")

            reply: str = send_to_jarvis(user_input)
                
            print(f"Jarvis: {reply}")
            speak_neral(reply)
            
    except KeyboardInterrupt:
        print("\nJarvis: Shutting down. Goodbye, sir!")
        speak_neral("Shutting down. Goodbye, sir!")