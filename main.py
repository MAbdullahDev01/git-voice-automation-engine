import argparse
import sys

try:
    from core.jarvis import send_to_jarvis
    from core.router import route_command
except Exception as exc:  # pragma: no cover - runtime fallback
    send_to_jarvis = None
    route_command = None
    ROUTER_IMPORT_ERROR = exc
else:
    ROUTER_IMPORT_ERROR = None

try:
    from tools.spotify_tools import play_music, pause_music, skip_track, previous_track
except Exception as exc:  # pragma: no cover - runtime fallback
    play_music = pause_music = skip_track = previous_track = None
    SPOTIFY_IMPORT_ERROR = exc
else:
    SPOTIFY_IMPORT_ERROR = None

try:
    from tools.git_tools import (
        cancel_git_commit,
        execute_git_commit,
        generate_git_commit_message,
        git_create_branch,
        git_current_branch,
        git_delete_branch,
        git_list_branches,
        git_switch_branch,
    )
except Exception as exc:  # pragma: no cover - runtime fallback
    git_commit = git_create_branch = git_current_branch = git_delete_branch = git_list_branches = git_switch_branch = None
    GIT_IMPORT_ERROR = exc
else:
    GIT_IMPORT_ERROR = None


PENDING_COMMIT_MSG = None


def speak_text(text: str) -> None:
    try:
        from audio.test_piper import speak_neral
        speak_neral(text)
    except Exception as exc:
        print(f"Speech output unavailable: {exc}")


def listen_for_input() -> str:
    try:
        from audio.test_ears import listen_neural
        return listen_neural()
    except Exception as exc:
        print(f"Speech input unavailable: {exc}")
        return ""


def process_pipeline(user_input: str, interactive: bool = True):
    global PENDING_COMMIT_MSG

    try:
        print(f"\n[User Input]: {user_input}")

        # Handle pending commit confirmation before routing new intent
        if PENDING_COMMIT_MSG is not None:
            choice = user_input.strip().lower()
            if choice in ["y", "yes"]:
                commit_message = PENDING_COMMIT_MSG
                PENDING_COMMIT_MSG = None
                return execute_git_commit(commit_message)

            PENDING_COMMIT_MSG = None
            return cancel_git_commit()

        if user_input in ["quit", "exit", "bye"]:
            raise KeyboardInterrupt

        # 1. Send to Router Model
        if route_command is None:
            payload = {"intent": "general_chat", "query": user_input}
            print(f"Router unavailable ({ROUTER_IMPORT_ERROR}). Falling back to general chat.")
        else:
            payload = route_command(user_input)
        
        intent = payload.get("intent")
        query = payload.get("query")
        
        print(f"[Router Output] Intent: '{intent}' | Query: '{query}'")

        response_text = None
        
        # 2. Match/Case Switch Routing
        match intent:
            case "git_commit":
                print("Triggering Git Commit Tooling...")
                if generate_git_commit_message is None:
                    response_text = "Git tools are unavailable in this environment."
                elif not interactive:
                    commit_msg = generate_git_commit_message(query if query else user_input)
                    if not commit_msg:
                        response_text = "No changes detected to commit."
                    else:
                        PENDING_COMMIT_MSG = commit_msg
                        response_text = f'Proposed Commit Message:\n"{commit_msg}"\n\nDo you want to proceed with this commit? (y/n)'
                elif interactive:
                    commit_msg = generate_git_commit_message(query if query else user_input)
                    if not commit_msg:
                        response_text = "No changes detected to commit."
                    else:
                        print(f"\nGenerated Commit Message:\n--> {commit_msg}")
                        confirm = input("Proceed with commit? (y/n): ").strip().lower()
                        if confirm == "y":
                            response_text = execute_git_commit(commit_msg)
                        else:
                            response_text = cancel_git_commit()

            case "git_create_branch":
                if git_create_branch is None:
                    response_text = "Git tools are unavailable in this environment."
                elif query:
                    git_create_branch(query)
                    response_text = f"Created and switched to branch: '{query}'"
                else:
                    response_text = "Please specify a branch name to create."

            case "git_switch_branch":
                if git_switch_branch is None:
                    response_text = "Git tools are unavailable in this environment."
                elif query:
                    git_switch_branch(query)
                    response_text = f"Switched to branch: '{query}'"
                else:
                    response_text = "Please specify a branch name to switch to."

            case "git_delete_branch":
                if git_delete_branch is None:
                    response_text = "Git tools are unavailable in this environment."
                elif query:
                    git_delete_branch(query)
                    response_text = f"Deleted branch: '{query}'"
                else:
                    response_text = "Please specify a branch name to delete."

            case "git_list_branches":
                if git_list_branches is None:
                    response_text = "Git tools are unavailable in this environment."
                else:
                    branches = git_list_branches()
                    response_text = "Local Branches:\n" + "\n".join(f" - {branch}" for branch in branches)

            case "git_current_branch":
                if git_current_branch is None:
                    response_text = "Git tools are unavailable in this environment."
                else:
                    current_branch = git_current_branch()
                    response_text = f"Current branch: {current_branch}"

            case "general_chat":
                print(f"Query enhanced into professional prompt:\n--> {query}")
                response = send_to_jarvis(query) if send_to_jarvis is not None else "JARVIS model is unavailable in this environment."
                print(f"Jarvis: {response}")
                speak_text(response)
                response_text = response

            case "spotify_play":
                if play_music is None:
                    response_text = "Spotify integration is unavailable in this environment."
                else:
                    play_music(query if query else "")
                    response_text = f"Playing music{f': {query}' if query else ''}."

            case "spotify_pause":
                if pause_music is None:
                    response_text = "Spotify integration is unavailable in this environment."
                else:
                    pause_music()
                    response_text = "Playback paused."

            case "spotify_skip":
                if skip_track is None:
                    response_text = "Spotify integration is unavailable in this environment."
                else:
                    skip_track()
                    response_text = "Skipped to the next track."

            case "spotify_previous":
                if previous_track is None:
                    response_text = "Spotify integration is unavailable in this environment."
                else:
                    previous_track()
                    response_text = "Went back to the previous track."

            case _:
                print("Unknown intent. Passing to fallback handler.")
                response = send_to_jarvis(user_input) if send_to_jarvis is not None else "JARVIS model is unavailable in this environment."
                print(f"Jarvis: {response}")
                speak_text(response)
                response_text = response
    except KeyboardInterrupt:
            print("\nJarvis: Shutting down. Goodbye, sir!")
            speak_text("Shutting down. Goodbye, sir!")

    return response_text


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run JARVIS in CLI or window mode")
    parser.add_argument("--cli", action="store_true", help="Run the terminal-based CLI instead of the window UI")
    parser.add_argument("--window", action="store_true", help="Run the window UI (default)")
    args = parser.parse_args(argv)

    if args.cli and args.window:
        raise SystemExit("Choose either --cli or --window, not both.")

    if args.cli:
        run_cli()
        return

    try:
        from PyQt6.QtWidgets import QApplication
        from app import JarvisMainWindow
    except ModuleNotFoundError:
        print("PyQt6 is not installed. Falling back to CLI mode.")
        run_cli()
        return

    app = QApplication(sys.argv)
    window = JarvisMainWindow()
    window.show()
    sys.exit(app.exec())


def run_cli():
    user_input: str
    
    try:
        while True:
            user_input = input("\nYou (type text or press Enter to talk): ").strip()
            
            # Handle exit conditions upfront
            if user_input.lower() in ["quit", "exit", "bye"]:
                raise KeyboardInterrupt
            
            # Trigger STT listening if input is empty (User pressed Enter)
            elif user_input == "":
                user_input = listen_for_input().strip()
                if not user_input:
                    continue
                print(f"You (Spoke): {user_input}")

            # Route the user input through the new AI classification pipeline
            process_pipeline(user_input)

    except KeyboardInterrupt:
        print("\nJarvis: Shutting down. Goodbye, sir!")
        speak_text("Shutting down. Goodbye, sir!")


if __name__ == "__main__":
    main()