#!/usr/bin/env python3

"""Generate templates for import into an assessment JSON with the PCA Wizard.

Usage:
  pca-wizard-templates (--emails | --targets)
  pca-wizard-templates (-h | --help)
  pca-wizard-templates --version
Options:
  -e --emails   Output a JSON template file for phishing emails.
  -t --targets  Output a CSV template file for phishing targets.
  -h --help     Show this screen.
  --version     Show version.
"""

# Standard Python Libraries
import json
from typing import Dict

# Third-Party Libraries
from docopt import docopt

from ._version import __version__

EMAIL_TEMPLATE = {
    "id": "Database ID",
    "from_address": "John Doe <john.doe@domain.tld>",
    "subject": "Subject",
    "html": '<div><div id="body"><p> </p></div></div>',
    "text": "",
}

TARGET_TEMPLATE = "First Name,Last Name,Email,Position"


def email_output():
    """Output an email JSON template."""
    print('Saving "template_emails.json"...')
    with open("template_email.json", "w") as fp:
        json.dump(EMAIL_TEMPLATE, fp, indent=4)


def targets_output():
    """Output a target emails CSV."""
    print('Saving "template_targets.csv"...')
    with open("template_targets.csv", "w") as fp:
        fp.write(TARGET_TEMPLATE)


def main():
    """Execute either email_output() or targets_output()."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

    if args["--emails"]:
        email_output()
    elif args["--targets"]:
        targets_output()


if __name__ == "__main__":
    main()
