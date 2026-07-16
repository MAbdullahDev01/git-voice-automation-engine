import requests as r

from test_piper import speak_neral

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:1.5b"

def send_to_jarvis(user_message : str) -> str:

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
            user_input = input("You: ").strip().lower()
            if user_input == "quit":
                print("\n Jarvis: Shutting down. Goodbye, sir!")
                speak_neral("Shutting down. Goodbye, sir!")
                break
            elif user_input == "":
                continue
            else:
                reply : str = send_to_jarvis(user_input)
                if reply == "Error: Cannot connect to Ollama. Make sure the application is running in your system tray.":
                    print(reply)
                    break
            print(f"Jarvis: {reply}")
            speak_neral(reply)
    except KeyboardInterrupt:
        print("\n Jarvis: Shutting down. Goodbye, sir!")
        speak_neral("Shutting down. Goodbye, sir!")