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
  * The test assessment is an exact copy of the real assessment that
  will be immediately sent to the custom targets provided in this
  tool.
"""

# Standard Python Libraries
import logging
import sys

# Third-Party Libraries
from docopt import docopt

# No type stubs exist for gophish, so we add "type: ignore" to tell mypy to
# ignore this library
from gophish.models import SMTP, Campaign, Group, Page, Template, User  # type: ignore
import urllib3

# cisagov Libraries
from tools.connect import connect_api
from util.input import get_input
from util.validate import validate_email

from ._version import __version__

# Disable "Insecure Request" warning: Gophish uses a self-signed certificate
# as default for https connections, which can not be  verified by a third
# party; thus, an SSL insecure request warning is produced.
#
# Without the noqa comment flake8 generates a DUO131 error because
# disabling this warning allows for the possibility of insecure
# connections.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # noqa: DUO131


def get_campaigns(api, assessment_id):
    """Return a list of all campaigns in an assessment."""
    logging.info("Gathering Campaigns")
    all_campaigns = api.campaigns.get()
    assessment_campaigns = []

    for campaign in all_campaigns:
        if campaign.name.startswith(assessment_id):
            assessment_campaigns.append(campaign)

    # Sets err to true if assessmentCampaigns has 0 length.
    logging.debug("Num Campaigns: %d", len(assessment_campaigns))
    if not len(assessment_campaigns):
        logging.warning("No Campaigns found for %s", assessment_id)

    return assessment_campaigns


def add_group(api, assessment_id):
    """Create a test group."""
    logging.info("Adding Test Group")

    new_group = Group()

    new_group.name = "Test-" + assessment_id

    # Holds list of Users to be added to group.
    targets = []

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

    new_group.targets = targets

    new_group = api.groups.post(new_group)

    return new_group.name


def campaign_test(api, assessment_campaigns, assessment_id):
    """Create test campaigns."""
    temp_groups = [Group(name=add_group(api, assessment_id))]

    for campaign in assessment_campaigns:
        temp_url = campaign.url
        temp_name = "Test-" + campaign.name
        temp_page = Page(name=campaign.page.name)
        temp_template = Template(name=campaign.template.name)
        temp_smtp = SMTP(name=campaign.smtp.name)

        post_campaign = Campaign(
            name=temp_name,
            groups=temp_groups,
            page=temp_page,
            template=temp_template,
            smtp=temp_smtp,
            url=temp_url,
        )

        post_campaign = api.campaigns.post(post_campaign)
        logging.debug("Test Campaign added: %s", post_campaign.name)

    logging.info("All Test campaigns added.")

    return True


def main() -> None:
    """Set up logging, connect to API, load all test data."""
    args: dict[str, str] = docopt(__doc__, version=__version__)

    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="\n%(levelname)s: %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            '"%s" is not a valid logging level.  Possible values are '
            "debug, info, warning, and error.",
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

    assessment_campaigns = get_campaigns(api, args["ASSESSMENT_ID"])

    if len(assessment_campaigns) > 0:
        campaign_test(api, assessment_campaigns, args["ASSESSMENT_ID"])

    # Stop logging and clean up
    logging.shutdown()
