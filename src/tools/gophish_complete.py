#!/usr/bin/env python3

"""GoPhish Campaign Completion tool for a Phishing Campaign Assessment (PCA).

User interface to select a campaign to complete or view a summery.  If auto
flag is provided with a CAMPAIGN_ID that campaign will be completed.

Usage:
  gophish-complete (--auto=CAMPAIGN_ID | --complete | --summary ) [--log-level=LEVEL] SERVER API_KEY
  gophish-complete (-h | --help)
  gophish-complete --version

Options:
  API_KEY                   API Access Key.
  SERVER                    Full URL to GoPhish server.
  -a --auto=CAMPAIGN_ID     Complete a specific campaign identified by CAMPAIGN_ID.
  -c --complete             Complete Campaign and show summary.
  -s --summary              Displays Campaign Summary.
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

from ._version import __version__

# Support Insecure Request waring.
requests.packages.urllib3.disable_warnings()


def get_campaigns(api):
    """Return a dictionary containing all campaigns."""
    allCampaigns = api.campaigns.get()

    while True:
        # Bandit complains about the input() function, but it is safe to
        # use in Python 3, which is required by this project.
        assessment_id = input("Enter Assessment ID: ")  # nosec
        assessmentCampaigns = dict()

        for campaign in allCampaigns:
            if campaign.name.startswith(assessment_id):
                assessmentCampaigns[campaign.id] = campaign.name

        if len(assessmentCampaigns):
            break
        else:
            logging.warning(
                "No Campaigns found for Assessment {}".format(assessment_id)
            )
            print("Please try again...")

    return assessmentCampaigns


def select_campaigns(campaigns):
    """Return the ID of a selected campaign."""
    print("Please select a Campaign ID:")
    print("\tID: Name")

    for key, name in campaigns.items():
        print("\t" + str(key) + ": " + name)

    print("")

    while True:
        # Bandit complains about the input() function, but it is safe to
        # use in Python 3, which is required by this project.
        inputId = input("ID: ")  # nosec
        if int(inputId) in campaigns:
            break
        else:
            logging.warning("Bad Campaign ID")
            print("Try again...")

    return inputId


def complete_campaign(api, api_key, server, workingID):
    """Complete a campaign."""
    url = f"{server}/api/campaigns/{workingID}/complete?api_key={api_key}"

    # Bandit complains about disabling the SSL certificate check, but we have
    # no choice here since we are using a self-signed certificate.
    response = requests.get(url=url, verify=False)  # nosec

    print("\n" + response.json()["message"])

    print_summary(api, workingID)

    return True


def print_summary(api, workingID):
    """Print a campaign summary."""
    summary = api.campaigns.summary(campaign_id=workingID)

    print("Campaign Summary:")
    print("\tName: " + summary.name)
    print("\tStatus: " + summary.status)
    print("\tLaunch Date: " + summary.launch_date)
    print("\tCompleted Date: " + summary.completed_date)
    print("\tTotal Users: " + str(summary.stats.total))
    print("\tTotal Sent: " + str(summary.stats.sent))
    print("\tTotal Clicks: " + str(summary.stats.clicked))

    return True


def main():
    """Set up logging, connect to API, call requested function(s)."""
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

    if args["--complete"]:
        campaigns = get_campaigns(api)
        workingID = select_campaigns(campaigns)
        success = complete_campaign(api, args["API_KEY"], args["SERVER"], workingID)

    elif args["--summary"]:
        campaigns = get_campaigns(api)
        workingID = select_campaigns(campaigns)
        success = print_summary(api, workingID)

    elif args["--auto"]:
        success = complete_campaign(
            api, args["API_KEY"], args["SERVER"], args["--auto"]
        )

    if not success:
        sys.exit(-1)


if __name__ == "__main__":
    main()
