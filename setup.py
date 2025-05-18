from setuptools import setup

setup(
    name = "ohgit",
    version = "0.1.0",
    author = "bhavyaprobably",
    packages = ["ohgit"],
    entry_points = {
        "console_scripts": [
            "ohgit = ohgit.cli:main"
        ]
    }
)