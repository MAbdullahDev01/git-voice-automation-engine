from utils.test_piper import speak_neral
from utils.test_ears import listen_neural
from utils.jarvis import send_to_jarvis
from utils.git_tools import git_commit, git_create_branch, git_current_branch, git_delete_branch, git_list_branches, git_switch_branch

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
                case _ if "create branch" in user_input:
                    branch_name = user_input.split("create branch")[-1].strip()
                    if branch_name:
                        git_create_branch(branch_name)
                    else:
                        print("Please specify a branch name to create.")
                case _ if "switch branch" in user_input:
                    branch_name = user_input.split("switch branch")[-1].strip()
                    if branch_name:
                        git_switch_branch(branch_name)
                    else:
                        print("Please specify a branch name to switch to.")
                case _ if "delete branch" in user_input:
                    branch_name = user_input.split("delete branch")[-1].strip()
                    if branch_name:
                        git_delete_branch(branch_name)
                    else:
                        print("Please specify a branch name to delete.")
                case _ if "list branches" in user_input:
                    branches = git_list_branches()
                    for branch in branches:
                        print(branch)
                case _ if "current branch" in user_input:
                    current_branch = git_current_branch()
                    print(f"Current branch: {current_branch}")

                case _:
                    reply = send_to_jarvis(user_input)
                    print(f"Jarvis: {reply}")
                    speak_neral(reply)

    except KeyboardInterrupt:
        print("\nJarvis: Shutting down. Goodbye, sir!")
        speak_neral("Shutting down. Goodbye, sir!")

if __name__ == "__main__":
    main()