#!/usr/bin/env python3

"""Remove an assessment or elements of an assessment in GoPhish.

Usage:
  gophish-cleaner (--assessment | --campaigns | --groups | --pages | --smtp | --templates) [--log-level=LEVEL] ASSESSMENT_ID SERVER API_KEY
  gophish-cleaner (-h | --help)
  gophish-cleaner --version

Options:
  API_KEY                   GoPhish API key.
  ASSESSMENT_ID             ID of the assessment to remove data from.
  SERVER                    Full URL to GoPhish server.
  -a --assessment           Remove all data for the specified assessment.
  -c --campaigns            Remove all campaigns from the specified assessment.
  -g --groups               Remove all users and groups from the specified assessment.
  -p --pages                Remove all landing pages from the specified assessment.
  -s --smtp                 Remove all sender profiles from the specified assessment.
  -t --templates            Remove all email templates from the specified assessment.
  -h --help                 Show this screen.
  --version                 Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""

# import IPython; IPython.embed() #<<< BREAKPOINT >>>
# sys.exit(0)

# Standard Python Libraries
import logging
import sys
from typing import Dict

# Third-Party Libraries
from docopt import docopt
import requests

# cisagov Libraries
from tools.connect import connect_api
from util.utils import match_assessment_id

from ._version import __version__

# Disable "Insecure Request" warning: GoPhish uses a self-signed certificate
# as default for https connections, which can not be  verified by a third
# party; thus, an SSL insecure request warning is produced.
requests.packages.urllib3.disable_warnings()


def confirm_id(element, assessment_id):
    """Display confirmation message and return response."""
    while True:
        if element != "assessment":
            logging.warning(
                "NOTE: THIS WILL REMOVE ALL {} DATA ASSOCIATED WITH ASSESSMENT {}".format(
                    element.upper(), assessment_id
                )
            )
            # Bandit complains about the input() function, but it is safe to
            # use in Python 3, which is required by this project.
            confirm = input("Is this really what you want to do?(y/n) ")  # nosec

        else:
            logging.warning(
                "NOTE: THIS WILL REMOVE ALL DATA ASSOCIATED WITH ASSESSMENT {}".format(
                    assessment_id
                )
            )
            # Bandit complains about the input() function, but it is safe to
            # use in Python 3, which is required by this project.
            confirm = input("Is this really what you want to do?(y/n) ")  # nosec

        if confirm.lower() == "y":
            return True

        else:
            return False


def remove_assessment(api, assessment_id):
    """Remove all elements of an assessment."""
    if (
        not remove_campaigns(api, assessment_id)
        or not remove_smtp(api, assessment_id)
        or not remove_group(api, assessment_id)
        or not remove_template(api, assessment_id)
        or not remove_page(api, assessment_id)
    ):
        success = False

    else:
        logging.info("Successfully removed all elements of {}".format(assessment_id))
        success = True

    return success


def remove_campaigns(api, assessment_id):
    """Remove all campaigns from an assessment."""
    allCampaigns = api.campaigns.get()

    for campaign in allCampaigns:
        if match_assessment_id(assessment_id, campaign.name):
            api.campaigns.delete(campaign.id)

    return True


def remove_smtp(api, assessment_id):
    """Remove all SMTP from an assessment."""
    allSMTP = api.smtp.get()

    for smtp in allSMTP:
        if match_assessment_id(assessment_id, smtp.name):
            api.smtp.delete(smtp.id)

    return True


def remove_page(api, assessment_id):
    """Remove all pages from an assessment."""
    allPages = api.pages.get()

    for page in allPages:
        if match_assessment_id(assessment_id, page.name):
            api.pages.delete(page.id)

    return True


def remove_group(api, assessment_id):
    """Remove all groups from an assessment."""
    allGroups = api.groups.get()

    for group in allGroups:
        if match_assessment_id(assessment_id, group.name):
            api.groups.delete(group.id)

    return True


def remove_template(api, assessment_id):
    """Remove all templates from an assessment."""
    allTemplates = api.templates.get()

    for template in allTemplates:
        if match_assessment_id(assessment_id, template.name):
            api.templates.delete(template.id)

    return True


def main():
    """Set up logging, connect to API, remove assessment data."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="\n%(levelname)s: %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            '"{}"is not a valid logging level.  Possible values are debug, info, warning, and error.'.format(
                log_level
            )
        )
        return 1

    else:
        # Connect to API
        try:
            api = connect_api(args["API_KEY"], args["SERVER"])
            logging.debug("Connected to: {}".format(args["SERVER"]))
        except Exception as e:
            logging.critical(print(e.args[0]))
            sys.exit(1)

    assessment_id = args["ASSESSMENT_ID"]

    if args["--campaigns"] and confirm_id("CAMPAIGNS", assessment_id):
        success = remove_campaigns(api, assessment_id)

    elif args["--smtp"] and confirm_id("SMTPS", assessment_id):
        success = remove_smtp(api, assessment_id)

    elif args["--pages"] and confirm_id("PAGES", assessment_id):
        success = remove_page(api, assessment_id)

    elif args["--groups"] and confirm_id("GROUPS", assessment_id):
        success = remove_group(api, assessment_id)

    elif args["--templates"] and confirm_id("TEMPLATES", assessment_id):
        success = remove_template(api, assessment_id)

    elif args["--assessment"] and confirm_id("assessment", assessment_id):
        success = remove_assessment(api, assessment_id)

    else:
        success = False

    if not success:
        sys.exit(-1)


if __name__ == "__main__":
    main()
