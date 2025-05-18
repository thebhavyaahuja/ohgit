import os

GIT_DIR = ".ohgit"

def init():
    """
    Initialize a new OhGit repository.
    """
    # Check if the current directory is already a Git repository
    if os.path.exists(GIT_DIR):
        print(f"Error: {GIT_DIR} already exists. This directory is already a Git repository.")
        return

    # Create the .ohgit directory
    os.makedirs(GIT_DIR, exist_ok=True)
    print(f"Initialized empty OhGit repository in {os.getcwd()}/{GIT_DIR}")