import os
import hashlib

GIT_DIR = ".ohgit"

def init():
    """
    Initialize a new OhGit repository.
    """
    # Check if the current directory is already a Git repository
    if os.path.exists(GIT_DIR):
        print(f"Error: {GIT_DIR} already exists. This directory is already a Git repository.")
        if os.path.exists(f"{GIT_DIR}/objects"):
            print(f"Error: {GIT_DIR}/objects already exists. This directory is already a Git repository.")
            return
        else:
            os.makedirs(f'{GIT_DIR}/objects', exist_ok=True)
            return
    else:
        os.makedirs(GIT_DIR, exist_ok=True)
        print(f"Initialized empty OhGit repository in {os.getcwd()}/{GIT_DIR}")
        os.makedirs(f'{GIT_DIR}/objects', exist_ok=True)
        print(f"Initialized empty OhGit objects directory in {os.getcwd()}/{GIT_DIR}/objects")
        return


def hash_object(data):
    """
    Hash the given data and store it in the .ohgit/objects directory.
    """
    print(f"Hashing data: \n{data}")
    print()
    # Create a unique hash for the data
    sha1 = hashlib.sha1()
    sha1.update(data)
    oid = sha1.hexdigest()

    # Store the object in the .ohgit/objects directory
    with open(f"{GIT_DIR}/objects/{oid}", "wb") as f:
        f.write(data)

    return oid