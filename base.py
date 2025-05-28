from . import data
import os
import itertools
import operator
from collections import namedtuple, deque
import string   

def init ():
    data.init ()
    data.update_ref ('HEAD', data.RefValue (symbolic=True, value='refs/heads/master'))


def write_tree(directory='.'):
    # Get the real basename of the directory we are about to scan.
    # This handles cases like 'directory' being '.' and the current working directory
    # being '.ohgit', or if 'directory' is explicitly '.ohgit'.
    entries = []
    print(f"Scanning directory: {directory}") # You can keep or remove debug prints
    with os.scandir(directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}' # Full path of the entry
            # Check if the entry (file or subdirectory) should be ignored
            if is_ignored(full):
                print(f"  Ignoring: {full} (in {directory})") # Debug print
                continue
            
            # Consider adding follow_symlinks=False for closer tutorial alignment
            if entry.is_file(follow_symlinks=False): 
                type_ = 'blob'
                with open(full, 'rb') as f:
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                type_ = 'tree'  
                oid = write_tree(full)
            else: # Handle cases where it's neither a file nor a directory (e.g., symlink to non-existent, etc.)
                continue # Or some other specific handling if needed

            entries.append((entry.name, oid, type_))

    # Create a tree object
    # Sort entries by name before creating the tree string
    # Use newline as separator as per tutorial
    tree_content_str = ''.join(f'{type_} {oid} {name}\n'
                               for name, oid, type_
                               in sorted(entries)) 
    return data.hash_object(tree_content_str.encode(), type_='tree')


def _iter_tree_entries(oid):
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(' ', 2)
        yield type_, oid, name

def get_tree (oid, base_path=''):
    result = {}
    for type_, oid, name in _iter_tree_entries (oid):
        assert '/' not in name
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            result.update (get_tree (oid, f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
        return result

def _empty_current_directory ():
    for root, dirnames, filenames in os.walk ('.', topdown=False):
        for filename in filenames:
            path = os.path.relpath (f'{root}/{filename}')
            if is_ignored (path) or not os.path.isfile (path):
                continue
            os.remove (path)
        for dirname in dirnames:
            path = os.path.relpath (f'{root}/{dirname}')
            if is_ignored (path):
                continue
            try:
                os.rmdir (path)
            except (FileNotFoundError, OSError):
                # Deletion might fail if the directory contains ignored files,
                # so it's OK
                pass

def read_tree (tree_oid):
    for path, oid in get_tree (tree_oid, base_path='./').items ():
        os.makedirs (os.path.dirname (path), exist_ok=True)
        with open (path, 'wb') as f:
            f.write (data.get_object (oid))

def commit (message):
    commit = f'tree {write_tree()}\n'

    HEAD = data.get_ref ('HEAD').value
    if HEAD:
        commit += f'parent {HEAD}\n'
    commit += '\n'
    commit += f'{message}\n'

    oid = data.hash_object (commit.encode (), 'commit')

    data.update_ref ('HEAD', data.RefValue (symbolic=False, value=oid))
    return oid

def is_ignored(name):
    # This correctly checks if '.ohgit' is a component of the path
    return '.ohgit' in name.split('/')

Commit = namedtuple('Commit', [ 'tree', 'parent', 'message' ])

def get_commit(oid):
    parent = None

    commit = data.get_object (oid, 'commit').decode()
    lines = iter(commit.splitlines())
    for line in itertools.takewhile (operator.truth, lines):
        key, value = line.split(' ', 1)
        if key == 'tree':
            tree = value
        elif key == 'parent':
            parent = value
        else:
            assert False, f'Unknown field {key}'

    message = '\n'.join (lines)
    return Commit (tree=tree, parent=parent, message=message)

def checkout (name):
    oid = get_oid (name)
    commit = get_commit (oid)
    read_tree (commit.tree)

    if is_branch (name):
        HEAD = data.RefValue (symbolic=True, value=f'refs/heads/{name}')
    else:
        HEAD = data.RefValue (symbolic=False, value=oid)

    data.update_ref ('HEAD', HEAD, deref=False)

def is_branch (branch):
    return data.get_ref (f'refs/heads/{branch}').value is not None

def create_tag (name, oid):
    data.update_ref (f'refs/tags/{name}', data.RefValue (symbolic=False, value=oid))

def get_oid (name):
    if name == '@': name = 'HEAD'

    # Try to get refs
    refs_to_try = [
        f'{name}',
        f'refs/{name}',
        f'refs/tags/{name}',
        f'refs/heads/{name}',
    ]
    for ref_path in refs_to_try:
        # data.get_ref(ref_path) by default dereferences fully and returns a RefValue
        # whose .value attribute should be the final OID string.
        ref_value_obj = data.get_ref(ref_path) 
        if ref_value_obj and ref_value_obj.value:
            # Ensure you return the .value which is the OID string
            return ref_value_obj.value 

    # Name is not a ref, presume it's an OID
    is_hex = all (c in string.hexdigits for c in name)
    if len (name) == 40 and is_hex:
        return name

    assert False, f'Unknown name {name}'

def iter_commits_and_parents (oids):
    oids = deque(oids)
    visited = set()

    while oids:
        oid = oids.popleft()
        if not oid or oid in visited:
            continue
        visited.add (oid)
        yield oid

        commit = get_commit (oid)
        oids.appendleft (commit.parent)

def create_branch (name, oid):
    data.update_ref (f'refs/heads/{name}', data.RefValue (symbolic=False, value=oid))

def get_branch_name():
    ref = data.get_ref('HEAD', deref=False)
    if ref.symbolic:
        return ref.value.split('/')[-1]  # Get the last part of the symbolic reference
    return None  # Not a branch, just an OID

def iter_branch_names ():
    for refname, _ in data.iter_refs ('refs/heads/'):
        yield os.path.relpath (refname, 'refs/heads/')