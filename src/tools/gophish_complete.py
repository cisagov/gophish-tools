#!/usr/bin/env python3

"""Complete a campaign in GoPhish and/or output a GoPhish campaign summary.

Usage:
  gophish-complete (--complete | --summary) [--Campaign=NAME] [--log-level=LEVEL] SERVER API_KEY
  gophish-complete (-h | --help)
  gophish-complete --version

Options:
  API_KEY                   GoPhish API key.
  SERVER                    Full URL to GoPhish server.
  -c --campaign=NAME        GoPhish campaign name.
  -c --complete             Complete a campaign within GoPhish.
  -s --summary              Output a summary of a GoPhish campaign.
  -h --help                 Show this screen.
  --version                 Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]

NOTE:
  * If a campaign name is not provided, all assessment campaigns will be listed to select from.
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
from util.input import get_input, get_number

from ._version import __version__

# Disable "Insecure Request" warning: GoPhish uses a self-signed certificate
# as default for https connections, which can not be  verified by a third
# party; thus, an SSL insecure request warning is produced.
requests.packages.urllib3.disable_warnings()


def get_campaign_id(campaign_name, campaigns):
    """Get campaign id from campaign name.

    Args:
        campaign_name (string): Full campaign name.
        campaigns (dict): Campaign id as key, campaign name as value.

    Raises:
        LookupError: Campaign name is not found in campaigns dictionary.

    Return:
        Campaign id corresponding to the campaign name provided.
    """
    for campaign_id, name_value in campaigns.items():
        if name_value == campaign_name:
            return campaign_id

    raise LookupError(f'Campaign name "{campaign_name}" not found.')


def get_campaigns(api, assessment_id):
    """Return a dictionary containing all campaigns.

    Args:
        api (GoPhish API): Connection to GoPhish server via the API.
        assessment_id (string): Assessment identifier to get campaigns from.

    Raises:
        LookupError: No campaigns found for the provided assessment id.

    Returns:
        dict: Campaign id as key, campaign name as value.
    """
    allCampaigns = api.campaigns.get()

    assessmentCampaigns = dict()

    for campaign in allCampaigns:
        if campaign.name.startswith(assessment_id):
            assessmentCampaigns[campaign.id] = campaign.name

    if len(assessmentCampaigns) == 0:
        raise LookupError(f"No campaigns found for assessment {assessment_id}")

    return assessmentCampaigns


def select_campaign(campaigns):
    """Return the ID of a selected campaign."""
    print("Please select a Campaign ID:")
    print("\tID: Name")

    for id, name in campaigns.items():
        print(f"\t {id}: {name}")

    print("")

    while True:
        inputId = get_number("ID: ")
        if inputId in campaigns:
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

    print(f'\n{response.json()["message"]}')

    print_summary(api, workingID)

    return True


def print_summary(api, workingID):
    """Print a campaign summary."""
    summary = api.campaigns.summary(campaign_id=workingID)

    print("Campaign Summary:")
    print(f"\tName: {summary.name}")
    print(f"\tStatus: {summary.status}")
    print(f"\tLaunch Date: {summary.launch_date}")
    print(f"\tCompleted Date: {summary.completed_date}")
    print(f"\tTotal Users: {summary.stats.total}")
    print(f"\tTotal Sent: {summary.stats.sent}")
    print(f"\tTotal Clicks:  {summary.stats.clicked}")

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
            f'"{log_level}"is not a valid logging level.  Possible values are debug, info, warning, and error.'
        )
        return 1

    # Connect to API
    try:
        api = connect_api(args["API_KEY"], args["SERVER"])
        logging.debug(f'Connected to: {args["SERVER"]}')
    except Exception as e:
        logging.critical(print(e.args[0]))
        sys.exit(1)

    # Gets assessment id from campaign name or user input.
    if not args["--Campaign"]:
        assessment_id = get_input("Enter the Assessment ID")
    else:
        # Sets assessment id from first section of campaign name. If the
        # assessment wizard is used to build the assessment the campaign
        # name will always start with the assessment identifier.
        assessment_id = args["--Campaign"].split("-")[0]

    # Gather all campaigns associated with assessment identifier.
    try:
        campaigns = get_campaigns(api, assessment_id)
        success = True
    except LookupError as err:
        logging.warning(err)
        success = False

    if args["--complete"] and success:
        if not args["--Campaign"]:
            workingID = select_campaign(campaigns)
        else:
            try:
                workingID = get_campaign_id(args["--Campaign"], campaigns)
            except LookupError as err:
                logging.warning(err)
                success = False

        if success and workingID:
            success = complete_campaign(api, args["API_KEY"], args["SERVER"], workingID)

    elif args["--summary"] and success:
        if not args["--Campaign"]:
            workingID = select_campaign(campaigns)
        else:
            try:
                workingID = get_campaign_id(args["--Campaign"], campaigns)
            except LookupError as err:
                logging.warning(err)
                success = False

        if success and workingID:
            success = print_summary(api, workingID)

    if not success:
        sys.exit(-1)


if __name__ == "__main__":
    main()
