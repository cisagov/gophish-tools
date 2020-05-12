#!/usr/bin/env python3

from util.validate import *
from util.input import *
from prompt_toolkit import prompt


def main():
    url = prompt("Campaign URL: ", default="domain", validator=BlankInputValidator())

    return url


if __name__ == "__main__":
    main()
