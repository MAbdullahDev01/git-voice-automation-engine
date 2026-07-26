from utils.test_piper import speak_neral
from utils.test_ears import listen_neural
from utils.jarvis import send_to_jarvis

def main():
    try:
        while True:
            user_input = input("You (type text or press Enter to talk): ").strip()
            if user_input.lower() == "quit":
                raise KeyboardInterrupt
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

if __name__ == "__main__":
    main()