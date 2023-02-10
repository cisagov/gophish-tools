"""Complete a campaign in Gophish and/or output a Gophish campaign summary.

Usage:
  gophish-complete [--campaign=NAME] [--summary-only] [--log-level=LEVEL] SERVER API_KEY
  gophish-complete (-h | --help)
  gophish-complete --version

Options:
  API_KEY                   Gophish API key.
  SERVER                    Full URL to Gophish server.
  -c --campaign=NAME        Gophish campaign name.
  -s --summary-only         Output a summary of a Gophish campaign.
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

# No type stubs exist for requests.packages.urllib3, so we add "type: ignore"
# to tell mypy to ignore this library
import requests.packages.urllib3  # type: ignore

# cisagov Libraries
from tools.connect import connect_api
from util.input import get_input, get_number

from ._version import __version__

# Disable "Insecure Request" warning: Gophish uses a self-signed certificate
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

    Returns:
        Campaign id corresponding to the campaign name provided.
    """
    for campaign_id, name_value in campaigns.items():
        if name_value == campaign_name:
            return campaign_id

    raise LookupError(f'Campaign name "{campaign_name}" not found.')


def get_campaigns(api, assessment_id=""):
    """Return a dictionary containing all campaigns.

    When called with a blank string for the assessment_id, the default value,
    all campaigns in all assessments will be returned. If an assessment_id is
    provided, then only the campaigns for that assessment will be returned.

    Args:
        api (Gophish API): Connection to Gophish server via the API.
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


def complete_campaign(api_key, server, campaign_id):
    """Complete a campaign in Gophish.

    Args:
        api_key (string): Gophish API key.
        server (string): Full URL to Gophish server.
        campaign_id (int): Gophish campaign id.

    Raises:
        UserWarning: Gophish is unsuccessful in completing the campaign.
    """
    url = f"{server}/api/campaigns/{campaign_id}/complete?api_key={api_key}"

    # Bandit complains about disabling the SSL certificate check, but we have
    # no choice here since we are using a self-signed certificate.
    response = requests.get(url=url, verify=False)  # nosec

    if not response.json()["success"]:
        raise UserWarning(response.json()["message"])
    else:
        print(f'\n{response.json()["message"]}')


def print_summary(api, campaign_id):
    """Print a campaign summary."""
    summary = api.campaigns.summary(campaign_id=campaign_id)

    print("Campaign Summary:")
    print(f"\tName: {summary.name}")
    print(f"\tStatus: {summary.status}")
    print(f"\tLaunch Date: {summary.launch_date}")
    print(f"\tCompleted Date: {summary.completed_date}")
    print(f"\tTotal Users: {summary.stats.total}")
    print(f"\tTotal Sent: {summary.stats.sent}")
    print(f"\tTotal Clicks:  {summary.stats.clicked}")

    return True


def main() -> None:
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
            '"%s" is not a valid logging level. Possible values are debug, info, warning, and error.',
            log_level,
        )
        sys.exit(1)

    # Connect to API
    try:
        api = connect_api(args["API_KEY"], args["SERVER"])
        logging.debug('Connected to: "%s"', args["SERVER"])
    except Exception as e:
        logging.critical(e.args[0])
        sys.exit(1)

    try:
        if args["--campaign"]:
            # Use campaign name to find campaign id.
            campaigns = get_campaigns(api)
            campaign_id = get_campaign_id(args["--campaign"], campaigns)
        else:
            # User inputs assessment id and selects campaign from lists.
            assessment_id = get_input("Enter the Assessment ID:")
            campaigns = get_campaigns(api, assessment_id)
            campaign_id = select_campaign(campaigns)

    except LookupError as err:
        logging.error(err)
        sys.exit(1)

    if args["--summary-only"]:
        # Output summary only.
        print_summary(api, campaign_id)
    else:
        # Complete and output summary.
        try:
            complete_campaign(args["API_KEY"], args["SERVER"], campaign_id)

        except UserWarning as err:
            logging.warning(err)
            sys.exit(1)

        print_summary(api, campaign_id)
