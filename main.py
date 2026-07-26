from utils.test_piper import speak_neral
from utils.test_ears import listen_neural
from utils.jarvis import send_to_jarvis
from utils.git_tools import git_commit

def main():

    # Type hinting
    user_input : str
    reply : str
    
    try:
        while True:
            user_input = input("You (type text or press Enter to talk): ").lower().strip()
            if user_input == "quit":
                raise KeyboardInterrupt
            elif user_input == "":
                user_input = listen_neural().lower().strip()
                if not user_input:
                    continue
                print(f"You (Spoke): {user_input}")

            match user_input:
                case "quit":
                    raise KeyboardInterrupt
                case _ if "commit changes" in user_input:
                    git_commit()

            reply = send_to_jarvis(user_input)

            print(f"Jarvis: {reply}")
            speak_neral(reply)

    except KeyboardInterrupt:
        print("\nJarvis: Shutting down. Goodbye, sir!")
        speak_neral("Shutting down. Goodbye, sir!")

if __name__ == "__main__":
    main()