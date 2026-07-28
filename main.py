from utils.test_piper import speak_neral
from utils.test_ears import listen_neural
from utils.jarvis import send_to_jarvis
from utils.git_commands import (
    git_commit, 
    git_create_branch, 
    git_current_branch, 
    git_delete_branch, 
    git_list_branches, 
    git_switch_branch
)
from utils.router import route_command


def process_pipeline(user_input: str):
    print(f"\n[User Input]: {user_input}")
    
    # 1. Send to Router Model
    payload = route_command(user_input)
    
    intent = payload.get("intent")
    query = payload.get("query")
    
    print(f"[Router Output] Intent: '{intent}' | Query: '{query}'")
    
    # 2. Match/Case Switch Routing
    match intent:
        case "git_commit":
            print("Triggering Git Commit Tooling...")
            git_commit(query if query else user_input)

        case "git_create_branch":
            if query:
                git_create_branch(query)
            else:
                print("Please specify a branch name to create.")

        case "git_switch_branch":
            if query:
                git_switch_branch(query)
            else:
                print("Please specify a branch name to switch to.")

        case "git_delete_branch":
            if query:
                git_delete_branch(query)
            else:
                print("Please specify a branch name to delete.")

        case "git_list_branches":
            branches = git_list_branches()
            print("Local Branches:")
            for branch in branches:
                print(f" - {branch}")

        case "git_current_branch":
            current_branch = git_current_branch()
            print(f"Current branch: {current_branch}")

        case "general_chat":
            print(f"💡 Query enhanced into professional prompt:\n--> {query}")
            response = send_to_jarvis(query)
            print(f"Jarvis: {response}")
            speak_neral(response)

        case _:
            print("⚠️ Unknown intent. Passing to fallback handler.")
            response = send_to_jarvis(user_input)
            print(f"Jarvis: {response}")
            speak_neral(response)


def main():
    user_input: str
    
    try:
        while True:
            user_input = input("\nYou (type text or press Enter to talk): ").lower().strip()
            
            # Handle exit conditions upfront
            if user_input in ["quit", "exit", "bye"]:
                raise KeyboardInterrupt
            
            # Trigger STT listening if input is empty (User pressed Enter)
            elif user_input == "":
                user_input = listen_neural().lower().strip()
                if not user_input:
                    continue
                print(f"You (Spoke): {user_input}")

            # Route the user input through the new AI classification pipeline
            process_pipeline(user_input)

    except KeyboardInterrupt:
        print("\nJarvis: Shutting down. Goodbye, sir!")
        speak_neral("Shutting down. Goodbye, sir!")


if __name__ == "__main__":
    main()