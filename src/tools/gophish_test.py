"""Send a duplicate assessment from Gophish to custom targets as a test.

Usage:
  Gophish-test [--log-level=LEVEL] ASSESSMENT_ID SERVER API_KEY
  Gophish-test (-h | --help)
  Gophish-test --version

Options:
  API_KEY                   Gophish API key.
  ASSESSMENT_ID             ID of the assessment to test.
  SERVER                    Full URL to Gophish server.
  -h --help                 Show this screen.
  --version                 Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]

NOTE:
  * The test assessment is an exact copy of the real assessment that will be immediately sent
  to the custom targets provided in this tool.
"""

# Standard Python Libraries
import logging
import sys
from typing import Dict

# Third-Party Libraries
from docopt import docopt
from gophish.models import SMTP, Campaign, Group, Page, Template, User
import requests.packages.urllib3

# cisagov Libraries
from tools.connect import connect_api
from util.input import get_input
from util.validate import validate_email

from ._version import __version__

# Disable "Insecure Request" warning: Gophish uses a self-signed certificate
# as default for https connections, which can not be  verified by a third
# party; thus, an SSL insecure request warning is produced.
requests.packages.urllib3.disable_warnings()


def get_campaigns(api, assessment_id):
    """Return a list of all campaigns in an assessment."""
    logging.info("Gathering Campaigns")
    allCampaigns = api.campaigns.get()
    assessmentCampaigns = list()

    for campaign in allCampaigns:
        if campaign.name.startswith(assessment_id):
            assessmentCampaigns.append(campaign)

    # Sets err to true if assessmentCampaigns has 0 length.
    logging.debug("Num Campaigns: %d", len(assessmentCampaigns))
    if not len(assessmentCampaigns):
        logging.warning("No Campaigns found for %s", assessment_id)

    return assessmentCampaigns


def add_group(api, assessment_id):
    """Create a test group."""
    logging.info("Adding Test Group")

    newGroup = Group()

    newGroup.name = "Test-" + assessment_id

    # Holds list of Users to be added to group.
    targets = list()

    target = User()
    target.first_name = get_input("Enter First Name: ")
    # Receives the file name and checks if it exists.
    while target.first_name != "done" or target.first_name == "":

        target.last_name = get_input("Enter Last Name: ")

        while True:
            target.email = get_input("Enter Email: ")
            if not validate_email(target.email):
                print("In Valid Email")
            else:
                break

        target.position = get_input("Enter Org: ")

        targets.append(target)

        target = User()
        target.first_name = get_input("Enter First Name or 'done': ")

    newGroup.targets = targets

    newGroup = api.groups.post(newGroup)

    return newGroup.name


def campaign_test(api, assessmentCampaigns, assessment_id):
    """Create test campaigns."""
    tempGroups = [Group(name=add_group(api, assessment_id))]

    for campaign in assessmentCampaigns:
        tempUrl = campaign.url
        tempName = "Test-" + campaign.name
        tempPage = Page(name=campaign.page.name)
        tempTemplate = Template(name=campaign.template.name)
        tempSmtp = SMTP(name=campaign.smtp.name)

        postCampaign = Campaign(
            name=tempName,
            groups=tempGroups,
            page=tempPage,
            template=tempTemplate,
            smtp=tempSmtp,
            url=tempUrl,
        )

        postCampaign = api.campaigns.post(postCampaign)
        logging.debug("Test Campaign added: %s", postCampaign.name)

    logging.info("All Test campaigns added.")

    return True


def main() -> None:
    """Set up logging, connect to API, load all test data."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="\n%(levelname)s: %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            '"%s" is not a valid logging level.  Possible values are debug, info, warning, and error.',
            log_level,
        )
        sys.exit(1)

    # Connect to API
    try:
        api = connect_api(args["API_KEY"], args["SERVER"])
        logging.debug("Connected to: %s", args["SERVER"])
    except Exception as e:
        logging.critical(e.args[0])
        sys.exit(1)

    assessmentCampaigns = get_campaigns(api, args["ASSESSMENT_ID"])

    if len(assessmentCampaigns) > 0:
        campaign_test(api, assessmentCampaigns, args["ASSESSMENT_ID"])

    # Stop logging and clean up
    logging.shutdown()
