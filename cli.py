import argparse
import os

from . import data

def main():
    args = parse_args()
    args.func(args)

def parse_args():
    parser = argparse.ArgumentParser(description="OhGit CLI")
    
    commands = parser.add_subparsers(dest='command')
    commands.required = True

    init_parser = commands.add_parser('init', help='Initialize a new OhGit repository')
    init_parser.set_defaults(func=init)

    return parser.parse_args()

def init(args):
    # print("Initializing a new OhGit repository...")
    data.init()
