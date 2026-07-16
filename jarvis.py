import requests as r

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:1.5b"

def send_to_jarvis(user_user_input):

    payload : dict = {
        "model" : MODEL_NAME,
        "messages" : [{
            "role" : "user",
            "content" : user_user_input,
        }],
        "stream" : False
    }

    try:
        print("Jarvis is thinking...")
        response = r.post(url=OLLAMA_URL, json=payload)
        response_data = response.json()
        return response_data["message"]["content"]
    except r.exceptions.RequestException:
        print("Error: Cannot connect to Ollama. Make sure the application is running in your system tray.")

if __name__ == "__main__":
    try:
        while True:
            user_input = input("You: ").strip().lower()
            if user_input == "quit":
                break
            elif user_input == "":
                continue
            else:
                reply = send_to_jarvis(user_input)
            print(f"Jarvis: {reply}")
    except KeyboardInterrupt:
        print("\n Jarvis: Shutting down. Goodbye, sir!")