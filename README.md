# ohgit
A simplified Git clone written in Python.

## Overview

OhGit is a learning project designed to replicate some of the core functionalities of Git. It helps in understanding how version control systems work under the hood, including object storage, tree structures, and commit histories.

## Commands Supported

Below is a list of commands currently supported by OhGit:

### 1. `ohgit init`
   - **Usage:** `ohgit init`
   - **Description:** Initializes a new empty OhGit repository in the current directory.
   - **Implementation:** This command creates a `.ohgit` subdirectory in the current working directory. Inside `.ohgit`, it sets up an `objects` directory to store all versioned data (blobs, trees, commits) and a `HEAD` file, which will point to the OID of the current commit.

### 2. `ohgit hash <file_path>`
   - **Usage:** `ohgit hash <file_path>`
   - **Description:** Computes the hash of a given file and stores its content as a "blob" object in the OhGit object database. This is OhGit's way of adding raw file content to its storage.
   - **Implementation:** The command reads the specified file's content. It then prepends the string `blob\0` (where `\0` is a null byte) to this content, calculates the SHA-1 hash (Object ID or OID) of the combined data, and stores this combined data in a new file named after its OID within the `.ohgit/objects/` directory.

### 3. `ohgit cat-file <object_id>`
   - **Usage:** `ohgit cat-file <object_id>`
   - **Description:** Displays the content of an OhGit object (which can be a blob, tree, or commit) given its OID.
   - **Implementation:** It retrieves the object file from `.ohgit/objects/<object_id>`. The content of this file includes a type prefix (e.g., `blob\0`, `tree\0`, `commit\0`). The command strips this prefix and prints the actual object content to the standard output.

### 4. `ohgit write-tree`
   - **Usage:** `ohgit write-tree`
   - **Description:** Creates a "tree" object that represents the current state of the working directory. This tree object contains references (OIDs) to files (as blobs) and subdirectories (as other trees).
   - **Implementation:** The command recursively scans the current directory (ignoring `.ohgit` and other specified patterns). For each file, it creates a blob object using the logic similar to `ohgit hash`. For each subdirectory, it makes a recursive call to `write_tree`. It then compiles a list of entries (type, OID, name) for the current directory, sorts them, formats them into a specific string structure, and hashes this string (with a `tree\0` prefix) to create the tree object, storing it in `.ohgit/objects/`.

### 5. `ohgit read-tree <tree_object_id>`
   - **Usage:** `ohgit read-tree <tree_object_id>`
   - **Description:** Restores the working directory to match the state represented by the given tree OID. This will overwrite existing files and directories in the working directory (except for `.ohgit`).
   - **Implementation:** It first clears the current working directory (excluding `.ohgit`). Then, it fetches the specified tree object using its OID. It iterates through the entries in this tree: for blob entries, it retrieves the blob's content and writes it to a file; for tree entries, it creates a subdirectory and recursively calls `read_tree` for that subtree.

### 6. `ohgit commit -m "<message>"`
   - **Usage:** `ohgit commit -m "<your commit message>"`
   - **Description:** Records the current state of the working directory (as captured by `ohgit write-tree`) into a new "commit" object. This commit object includes the commit message, a pointer to the parent commit (if any), and a pointer to the root tree object.
   - **Implementation:** It first calls `write_tree()` to get the OID of the current directory's root tree. It then retrieves the OID of the parent commit from the `.ohgit/HEAD` file. A commit data string is constructed containing the tree OID, parent OID (if present), and the user's message. This string is then hashed (with a `commit\0` prefix) to create the commit object, which is stored in `.ohgit/objects/`. Finally, `.ohgit/HEAD` is updated to point to this new commit's OID.

### 7. `ohgit log [commit_object_id]`
   - **Usage:** `ohgit log [commit_object_id]`
   - **Description:** Displays the commit history. If a `commit_object_id` is provided, it starts the log from that commit; otherwise, it starts from the commit pointed to by `HEAD`.
   - **Implementation:** It starts with the specified OID (or the OID from `HEAD`). It retrieves the commit object, prints its OID and message. It then follows the `parent` OID stored within that commit object to find and display the previous commit, continuing this process until it reaches a commit with no parent (the initial commit).

### 8. `ohgit checkout <commit_object_id>`
   - **Usage:** `ohgit checkout <commit_object_id>`
   - **Description:** Updates the working directory to match the state of the project as recorded in the specified commit. It also updates `HEAD` to point to this commit.
   - **Implementation:** It retrieves the specified commit object to find the OID of its associated root tree. It then calls `read_tree` with this tree OID to repopulate the working directory. After successfully updating the working directory, it updates the `.ohgit/HEAD` file to store the OID of the checked-out commit.
