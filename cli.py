import argparse
import os
import sys
import textwrap
from . import data
from . import base

def main():
    args = parse_args()
    args.func(args)

def parse_args():
    parser = argparse.ArgumentParser(description="OhGit CLI")
    
    commands = parser.add_subparsers(dest='command')
    commands.required = True

    # Add subcommand for 'init'
    init_parser = commands.add_parser('init', help='Initialize a new OhGit repository')
    init_parser.set_defaults(func=init) 

    # Add subcommand for 'hash'
    hash_object_parser = commands.add_parser('hash', help='Hash an object and store it in the repository')
    hash_object_parser.add_argument('data', type=str, help='Data to hash')
    hash_object_parser.set_defaults(func=hash_object)

    # Add subcommand for 'cat-file'
    cat_file_parser = commands.add_parser('cat-file', help='Display the contents of a file in the repository')
    cat_file_parser.add_argument('oid', type=str, help='Object ID to display')
    cat_file_parser.set_defaults(func=cat_file)

    # Add subcommand for 'write-tree'
    write_tree_parser = commands.add_parser('write-tree', help='Write the current state of the working directory to the repository')
    write_tree_parser.set_defaults(func=write_tree)

    # Add subcommand for 'read-tree'
    read_tree_parser = commands.add_parser('read-tree', help='Read a tree object and write its contents to the working directory')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument('tree', type=str, help='Object ID of the tree to read')

    # Add subcommand for 'commit'
    commit_parser = commands.add_parser ('commit')
    commit_parser.set_defaults (func=commit)
    commit_parser.add_argument ('-m', '--message', required=True)

    log_parser = commands.add_parser ('log')
    log_parser.set_defaults (func=log)
    log_parser.add_argument ('oid', nargs='?')

    return parser.parse_args()

def init(args):
    # print("Initializing a new OhGit repository...")
    data.init()

def hash_object(args):
    # print(f"Hashing data: {args.data}")
    with open(args.data, 'rb') as f:
        file_content= f.read()
    oid = data.hash_object(file_content)
    print(f"Hashed object ID: {oid}")

def cat_file(args):
    # print(f"Displaying contents of object ID: {args.oid}")
    sys.stdout.flush()
    object_content = data.get_object(args.oid, expected=None)
    if object_content is not None:
        sys.stdout.buffer.write(object_content)

def write_tree(args):
    # print("Writing the current state of the working directory to the repository...")
    print(base.write_tree())
    print("Written the current state of the working directory to the repository.")

def read_tree(args):
    # print(f"Reading tree object ID: {args.tree}")
    base.read_tree(args.tree)
    print(f"Read tree object ID: {args.tree} and wrote its contents to the working directory.")

def commit(args):
    # print(f"Committing changes with message: {args.message}")
    base.commit(args.message)
    print(f"Committed changes with message: {args.message}")

def log(args):
    oid = args.oid or data.get_HEAD ()
    while oid:
        commit = base.get_commit (oid)

        print (f'commit {oid}\n')
        print (textwrap.indent (commit.message, '    '))
        print ('')

        oid = commit.parent