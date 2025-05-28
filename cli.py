import argparse
import os
import sys
import textwrap
from . import data
from . import base
import subprocess

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

    oid = base.get_oid

    # Add subcommand for 'hash'
    hash_object_parser = commands.add_parser('hash', help='Hash an object and store it in the repository')
    hash_object_parser.add_argument('data', type=str, help='Data to hash')
    hash_object_parser.set_defaults(func=hash_object)

    # Add subcommand for 'cat-file'
    cat_file_parser = commands.add_parser('cat-file', help='Display the contents of a file in the repository')
    cat_file_parser.add_argument ('object', type=oid)
    cat_file_parser.set_defaults(func=cat_file)

    # Add subcommand for 'write-tree'
    write_tree_parser = commands.add_parser('write-tree', help='Write the current state of the working directory to the repository')
    write_tree_parser.set_defaults(func=write_tree)

    # Add subcommand for 'read-tree'
    read_tree_parser = commands.add_parser('read-tree', help='Read a tree object and write its contents to the working directory')
    read_tree_parser.set_defaults(func=read_tree)
    read_tree_parser.add_argument ('tree', type=oid)

    # Add subcommand for 'commit'
    commit_parser = commands.add_parser ('commit')
    commit_parser.set_defaults (func=commit)
    commit_parser.add_argument ('-m', '--message', required=True)

    log_parser = commands.add_parser ('log')
    log_parser.set_defaults (func=log)
    log_parser.add_argument ('oid', default='@', type=oid, nargs='?')

    checkout_parser = commands.add_parser ('checkout')
    checkout_parser.set_defaults (func=checkout)
    checkout_parser.add_argument ('commit')

    tag_parser = commands.add_parser ('tag')
    tag_parser.set_defaults (func=tag)
    tag_parser.add_argument ('name')
    tag_parser.add_argument ('oid', default='@', type=oid, nargs='?')

    k_parser = commands.add_parser('k')
    k_parser.set_defaults (func=k)

    branch_parser = commands.add_parser ('branch')
    branch_parser.set_defaults (func=branch)
    branch_parser.add_argument ('name',nargs='?')
    branch_parser.add_argument ('start_point', default='@', type=oid, nargs='?')

    status_parser = commands.add_parser ('status')
    status_parser.set_defaults (func=status)

    reset_parser = commands.add_parser ('reset')
    reset_parser.set_defaults (func=reset)
    reset_parser.add_argument ('commit', type=oid)

    return parser.parse_args()

def init(args):
    # print("Initializing a new OhGit repository...")
    base.init()

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
    refs = {}
    for refname, ref in data.iter_refs ():
        refs.setdefault (ref.value, []).append (refname)
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'
    for oid in base.iter_commits_and_parents ({args.oid}):
        commit = base.get_commit (oid)
        refs_str = f' ({", ".join (refs[oid])})' if oid in refs else ''
        print (f'commit {RED}{oid}{RESET}{refs_str}\n')
        print (textwrap.indent (f'{GREEN}{commit.message}{RESET}', '    '))
        print ('')

        oid = commit.parent

def checkout(args):
    base.checkout(args.commit)

def tag (args):
    base.create_tag (args.name, args.oid)

def k (args):
    dot = 'digraph commits {\n'

    oids = set ()
    for refname, ref in data.iter_refs (deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        if not ref.symbolic:
            oids.add (ref.value)

    for oid in base.iter_commits_and_parents (oids):
        commit = base.get_commit (oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        if commit.parent:
            dot += f'"{oid}" -> "{commit.parent}"\n'

    dot += '}'
    print (dot)

    # with subprocess.Popen (
    #         ['dot', '-Txdot', '/dev/stdin'],
    #         stdin=subprocess.PIPE) as proc:
    #     proc.communicate (dot.encode ())
    
    with subprocess.Popen (
            ['dot', '-Tpng', '-o', 'commits.png', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate (dot.encode ())

def branch(args):
    GREEN = '\033[91m'
    RESET = '\033[0m'

    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            if branch == current:
                # Star + current branch name in green
                print(f'* {GREEN}{branch}{RESET} current')
            else:
                print(f'  {branch}')
    else:
        base.create_branch(args.name, args.start_point)
        print(f"Created branch '{args.name}' starting from '{args.start_point}'")


def status(args):
    GREEN = '\033[91m'
    RESET = '\033[0m'
    HEAD = base.get_oid('@')
    branch = base.get_branch_name()
    if branch:
        print(f"On branch {GREEN}{branch}{RESET}")
    else:
        print(f'HEAD detached at {HEAD[:10]}')

def reset (args):
    base.reset (args.commit)
