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


def hash_object(data, type_="blob"):
    """
    Hash the given data and store it in the .ohgit/objects directory.
    """
    print(f"Hashing data: \n{data}")
    print()
    # Create a unique hash for the data
    object= type_.encode() + b"\0" + data
    sha1 = hashlib.sha1(object)
    oid = sha1.hexdigest()
    print(f"Object ID: {oid}")

    # Store the object in the .ohgit/objects directory
    with open(f"{GIT_DIR}/objects/{oid}", "wb") as f:
        f.write(object)

    return oid

def get_object(oid, expected="blob"):
    """
    Retrieve the object with the given OID from the .ohgit/objects directory.
    """
    # Check if the object exists
    if not os.path.exists(f"{GIT_DIR}/objects/{oid}"):
        print(f"Error: Object {oid} not found in {GIT_DIR}/objects")
        return None

    # Read and return the object data
    with open(f"{GIT_DIR}/objects/{oid}", "rb") as f:
        obj = f.read()
    type_from_file_bytes, content = obj.split(b"\0", 1)
    type_from_file_str = type_from_file_bytes.decode()


    if expected is not None:
        if type_from_file_str != expected:  # Ensure this is '!=' for a mismatch
            print(f"Error: Expected object type {expected}, but got {type_from_file_str}")
            return None
    return content


def update_ref (ref, oid):
    ref_path = f'{GIT_DIR}/{ref}'
    os.makedirs (os.path.dirname (ref_path), exist_ok=True)
    with open (ref_path, 'w') as f:
        f.write (oid)

def get_ref (ref):
    ref_path = f'{GIT_DIR}/{ref}'
    if os.path.isfile (ref_path):
        with open (ref_path) as f:
            return f.read ().strip ()

