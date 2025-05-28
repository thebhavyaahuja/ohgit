# ohgit
A simplified Git clone written in Python.

## Overview

OhGit is a learning project designed to replicate some of the core functionalities of Git. It helps in understanding how version control systems work under the hood, including object storage, tree structures, and commit histories.

run ts first gng :
```
export PATH="$HOME/.local/bin:$PATH"
```

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

### 7. 
```
ohgit log [commit_object_id]
```
   - **Usage:** `ohgit log [commit_object_id]`
   - **Description:** Displays the commit history. If a `commit_object_id` is provided, it starts the log from that commit; otherwise, it starts from the commit pointed to by `HEAD`.
   - **Implementation:** It starts with the specified OID (or the OID from `HEAD`). It retrieves the commit object, prints its OID and message. It then follows the `parent` OID stored within that commit object to find and display the previous commit, continuing this process until it reaches a commit with no parent (the initial commit).

### 8. `ohgit checkout <commit_object_id>`
   - **Usage:** `ohgit checkout <commit_object_id>`
   - **Description:** Updates the working directory to match the state of the project as recorded in the specified commit. It also updates `HEAD` to point to this commit.
   - **Implementation:** It retrieves the specified commit object to find the OID of its associated root tree. It then calls `read_tree` with this tree OID to repopulate the working directory. After successfully updating the working directory, it updates the `.ohgit/HEAD` file to store the OID of the checked-out commit.


### 9. `ohgit tag <tag_name> [commit_oid]`
   - **Usage:** `ohgit tag <tag_name> [commit_oid]`
   - **Description:** Creates a tag, which is a named, human-readable pointer to a specific commit. If `commit_oid` is omitted, the tag points to the commit currently referenced by `HEAD`.
   - **Implementation:** The command resolves the `commit_oid` (defaulting to the OID in `HEAD` if not provided). It then creates or updates a file at `.ohgit/refs/tags/<tag_name>`. The content of this file is simply the OID of the commit that the tag is pointing to.

### 10. `ohgit k`
    - **Usage:** `ohgit k`
    - **Description:** Visualizes the commit history, including branches and tags, as a graph. This command requires Graphviz to be installed.
    - **Implementation:** It gathers all references (like `HEAD` and all tags from `.ohgit/refs/tags/`) and their corresponding commit OIDs. It then traverses the commit history starting from these OIDs, collecting commit OIDs and their parent OIDs. A DOT language string is generated to describe this graph structure, which is then passed to the `dot` command-line tool (from Graphviz) via a subprocess to render and display the graph (e.g., using `xdot` for an interactive view or outputting to an image file).


### 11. `ohgit branch [branch_name] [start_point_oid]`
    - **Usage:**
        - `ohgit branch`: Lists all local branches, highlighting the current one.
        - `ohgit branch <branch_name> [start_point_oid]`: Creates a new branch named `<branch_name>` pointing to `start_point_oid`. If `start_point_oid` is omitted, it defaults to the current `HEAD`.
    - **Description:** Manages branches. Branches are movable pointers to commits, allowing for divergent lines of development.
    - **Implementation:**
        - Listing: Iterates through files in `.ohgit/refs/heads/` and prints their names. It determines the current branch by checking if `HEAD` is a symbolic ref to a branch.
        - Creation: Creates a new file at `.ohgit/refs/heads/<branch_name>` containing the OID of the `start_point_oid`.

### 12. `ohgit status`
    - **Usage:** `ohgit status`
    - **Description:** Displays the current branch or indicates if `HEAD` is detached. (Note: This is a simplified status and does not show uncommitted changes like Git).
    - **Implementation:** It retrieves the current branch name by checking if `HEAD` is a symbolic ref pointing to a branch in `refs/heads/`. If so, it prints the branch name. Otherwise, it prints the OID that `HEAD` is directly pointing to, indicating a detached `HEAD` state.

### 13. `ohgit reset <commit_oid>`
    - **Usage:** `ohgit reset <commit_oid>`
    - **Description:** Resets the current branch `HEAD` (if on a branch) or `HEAD` itself (if detached) to point to the specified `commit_oid`. This command only changes the `HEAD` pointer; it does not modify the working directory or staging area.
    - **Implementation:** It resolves the `<commit_oid>` to a full OID. It then updates the ref that `HEAD` points to (if `HEAD` is symbolic, e.g., `ref: refs/heads/main`, it updates `refs/heads/main`) or updates `HEAD` directly (if detached) to store the new `commit_oid`.
