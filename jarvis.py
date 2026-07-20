import requests as r

from test_piper import speak_neral
from test_ears import listen_neural

from config import OLLAMA_URL, MODEL_NAME

def send_to_jarvis(user_message : str) -> str:

    if not OLLAMA_URL or not MODEL_NAME:
        return "Error: Ollama configuration is missing. Check OLLAMA_URL and MODEL_NAME."

    payload : dict = {
        "model" : MODEL_NAME,
        "messages" : [{
            "role" : "user",
            "content" : user_message,
        }],
        "stream" : False
    }

    try:
        print("Jarvis is thinking...")
        response = r.post(url=OLLAMA_URL, json=payload)
        response_data = response.json()
        return response_data["message"]["content"]
    except r.exceptions.RequestException:
        return ("Error: Cannot connect to Ollama. Make sure the application is running in your system tray.")

if __name__ == "__main__":
    try:
        while True:
            user_input = input("You (type text or press Enter to talk): ").strip()
            if user_input.lower() == "quit":
                print("\n Jarvis: Shutting down. Goodbye, sir!")
                speak_neral("Shutting down. Goodbye, sir!")
                break
            elif user_input == "":
                user_input = listen_neural().strip()
                if user_input == "":
                    continue

            reply : str = send_to_jarvis(user_input)
            if reply == "Error: Cannot connect to Ollama. Make sure the application is running in your system tray.":
                print(reply)
                break
            print(f"Jarvis: {reply}")
            speak_neral(reply)
    except KeyboardInterrupt:
        print("\n Jarvis: Shutting down. Goodbye, sir!")
        speak_neral("Shutting down. Goodbye, sir!")