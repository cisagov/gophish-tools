"""Utility function to print out to stdout and file at the same time."""


def double_print(outfile, line_string):
    """Write to console and a file using the same string."""
    print(line_string)
    outfile.write(line_string + "\n")
