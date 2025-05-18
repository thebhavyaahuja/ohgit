import argparse
import os
import sys

from . import data

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