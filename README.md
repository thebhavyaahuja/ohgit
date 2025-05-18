# ohgit
My Git clone

## commands supported :

1. The `ohgit init` command creates a new empty repository.

Git stores all repository data locally, in a subdirectory called ".ohgit", so upon initialization we'll create one.

2. `ohgit hash <path_to_file_tbHashed>`

This command will take a file and store it in our .ugit directory for later retrieval.
The type of storage is content-addressable storage

3. `ohgit cat-file <oid>`
Read a file in /ohgit/objects/<oid>

