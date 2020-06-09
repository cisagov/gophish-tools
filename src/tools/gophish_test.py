#!/usr/bin/env python3

"""GoPhish Testing Module for a Phishing Campaign Assessment (PCA).

Usage:
  gophish-test [--log-level=LEVEL] ASSESSMENT_ID SERVER API_KEY
  gophish-test (-h | --help)
  gophish-test --version

Options:
  SERVER      Full URL to GoPhish server
  API_KEY      API Access Key
  ASSESSMENT_ID      Assessment ID to test.
  -h --help      Show this screen.
  --version      Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import logging
import sys

# Third-Party Libraries
from docopt import docopt
from gophish.models import SMTP, Campaign, Group, Page, Template, User
import requests

# cisagov Libraries
from tools.connect import connect_api
from util.input import get_input
from util.validate import validate_email

args = docopt(__doc__, version="v0.1")

# Support Insecure Request waring.
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
    logging.debug(f"Num Campaigns: {len(assessmentCampaigns)}")
    if not len(assessmentCampaigns):
        logging.warning("No Campaigns found for {}".format(assessment_id))

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


def campaign_test(api, assessmentCampaigns):
    """Create test campaigns."""
    tempGroups = [Group(name=add_group(api, args["ASSESSMENT_ID"]))]

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
        logging.debug("Test Campaign added: {}".format(postCampaign.name))

    logging.info("All Test campaigns added.")

    return True


def main():
    """Set up logging, connect to API, load all test data."""
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

    # Connect to API
    try:
        api = connect_api(args["API_KEY"], args["SERVER"])
        logging.debug("Connected to: {}".format(args["SERVER"]))
    except Exception as e:
        logging.critical(print(e.args[0]))
        sys.exit(1)

    assessmentCampaigns = get_campaigns(api, args["ASSESSMENT_ID"])

    if len(assessmentCampaigns) > 0:
        campaign_test(
            api, assessmentCampaigns,
        )

    # Stop logging and clean up
    logging.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
