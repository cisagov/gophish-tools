#!/usr/bin/env python3
"""The prompter module."""

# Third-Party Libraries
from prompt_toolkit import prompt

# cisagov Libraries
from util.validate import BlankInputValidator


def main():
    """Return a URL prompt."""
    url = prompt("Campaign URL: ", default="domain", validator=BlankInputValidator())

    return url


if __name__ == "__main__":
    main()
