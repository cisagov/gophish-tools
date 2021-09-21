"""Import an assessment JSON file into GoPhish.

Usage:
  gophish-import [--log-level=LEVEL] [--reschedule] ASSESSMENT_FILE SERVER API_KEY
  gophish-import (-h | --help)
  gophish-import --version

Options:
  API_KEY                   GoPhish API key.
  ASSESSMENT_FILE           Name of the JSON file containing assessment data.
  SERVER                    Full URL to GoPhish server.
  -r --reschedule           Adjust the current schedule of an assessment with the new schedule in the ASSESSMENT_FILE.
  -h --help                 Show this screen.
  --version                 Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import json
import logging
import sys
from typing import Dict

# Third-Party Libraries
from docopt import docopt
from gophish.models import SMTP, Campaign, Error, Group, Page, Template, User
import requests

# cisagov Libraries
from tools.connect import connect_api

from ._version import __version__

# Disable "Insecure Request" warning: GoPhish uses a self-signed certificate
# as default for https connections, which can not be  verified by a third
# party; thus, an SSL insecure request warning is produced.
requests.packages.urllib3.disable_warnings()


def load_landings(api, assessment):
    """Return all landing pages in an assessment."""
    pages = assessment["pages"]

    for page in pages:
        new_page = Page()
        new_page.name = page["name"]
        new_page.capture_credentials = page["capture_credentials"]
        new_page.capture_passwords = page["capture_passwords"]
        new_page.html = page["html"]
        if page["redirect_url"]:
            new_page.redirect_url = page["redirect_url"]

        # Debug page information, editors may produce a false error or warning for lines 57 - 60

        logging.debug("Page Name: %s", new_page.name)
        logging.debug("Redirect ULR: %s", new_page.redirect_url)
        logging.debug("Capture Credentials: %s", new_page.capture_credentials)
        logging.debug("Capture Passwords: %s", new_page.capture_passwords)

        """
         Catches when a page has already been loaded into GoPhish.
         Finds the current GoPhish page ID so it can be deleted
         prior to re-loading the new page.
        """
        while True:
            try:
                new_page = api.pages.post(new_page)
                break
            except Error as e:
                if e.message == "Page name already in use":
                    logging.warning("%s. Finding with previously loaded page.", e)
                    old_pages = api.pages.get()
                    for old_page in old_pages:
                        if old_page.name == new_page.name:
                            logging.debug("Deleting Page with ID %i", old_page.id)
                            api.pages.delete(old_page.id)
                            logging.info("Re-Loading new page.")
                else:
                    logging.error(f"{e}\n")
                    raise

        # Returns Landing Page ID
        logging.info("Landing Page %s loaded.", new_page.name)
        page["id"] = new_page.id

    return pages


def load_groups(api, assessment):
    """Return all groups in an assessment."""
    groups = assessment["groups"]

    for group in groups:
        logging.info("Loading Group %s", group["name"])

        new_group = Group()
        new_group.name = group["name"]

        for tgt in group["targets"]:
            target = User()
            target.first_name = tgt["first_name"]
            target.last_name = tgt["last_name"]
            target.email = tgt["email"]
            if tgt["position"]:
                target.position = tgt["position"]
            new_group.targets.append(target)

        """
         Catches when a Group has already been loaded into GoPhish.
         Finds the current GoPhish group ID so it can be deleted
         prior to re-loading the new group.
        """
        while True:
            try:
                new_group = api.groups.post(new_group)
                break
            except Error as e:
                if e.message == "Group name already in use":
                    logging.warning("%s. Finding previously loaded group to delete.", e)
                    groups = api.groups.get()
                    logging.debug(
                        "Checking %i for previously imported group to get ID",
                        len(groups),
                    )
                    for old_group in groups:
                        if old_group.name == new_group.name:
                            logging.debug("Deleting Group with ID %i", old_group.id)
                            api.groups.delete(old_group.id)
                            logging.info("Re-Loading new group.")
                else:
                    logging.error("%s", e)
                    raise

        group["id"] = new_group.id

        logging.info("Group Ready: %s", new_group.name)

    return groups


def build_campaigns(api, assessment):
    """Build campaigns."""
    logging.info("Building Campaigns.")
    for campaign in assessment["campaigns"]:
        logging.info("Building Campaign: %s", campaign["name"])

        # Build Template object
        new_template = Template(
            name=campaign["template"]["name"],
            subject=campaign["template"]["subject"],
            html=campaign["template"]["html"],
            text=campaign["template"]["text"],
        )

        """
         Catches when Template has already been loaded into GoPhish.
         Finds the current GoPhish template ID so it can be deleted
         prior to re-loading the new template.
        """
        while True:
            try:
                new_template = api.templates.post(new_template)
                break
            except Error as e:
                if e.message == "Template name already in use":
                    logging.warning(
                        "%s. Finding previously loaded template to delete.", e.message
                    )
                    templates = api.templates.get()
                    logging.debug(
                        "Checking %i for previously imported template to get ID",
                        len(templates),
                    )
                    for old_template in templates:
                        if old_template.name == new_template.name:
                            logging.debug(
                                "Deleting Template with ID %i", old_template.id
                            )
                            api.templates.delete(old_template.id)
                            logging.info("Re-Loading new template.")
                else:
                    logging.error("%s", e.message)
                    raise

        # Build SMTP Object
        new_smtp = SMTP(
            name=campaign["smtp"]["name"],
            host=campaign["smtp"]["host"],
            from_address=campaign["smtp"]["from_address"],
            interface_type="SMTP",
            ignore_cert_errors=True,
        )
        if (
            "username" in campaign["smtp"].keys()
            and "password" in campaign["smtp"].keys()
        ):
            new_smtp.username = campaign["smtp"]["username"]
            new_smtp.password = campaign["smtp"]["password"]

        while True:
            try:
                new_smtp = api.smtp.post(new_smtp)
                break
            except Error as e:
                if e.message == "SMTP name already in use":
                    logging.warning("%s. Finding previously loaded smtp to delete.", e)
                    smtps = api.smtp.get()
                    logging.debug(
                        "Checking %i for previously imported smtp profiles to get ID",
                        len(smtps),
                    )
                    for old_smtp in smtps:
                        if old_smtp.name == new_smtp.name:
                            logging.debug("Deleting SMTP with ID %i", old_smtp.id)
                            api.smtp.delete(old_smtp.id)
                            logging.info("Re-Loading new SMTP.")
                else:
                    logging.error("%s", e.message)
                    raise

        # Check to remove any campaigns with the same name
        old_campaigns = api.campaigns.get()
        for old_campaign in old_campaigns:
            if old_campaign.name == campaign["name"]:
                logging.warning(
                    "Previous Campaign found with name %s.", campaign["name"]
                )
                logging.warning(
                    "Previous Campaign with id %i being deleted.", old_campaign.id
                )
                api.campaigns.delete(old_campaign.id)

        # Loads the campaign
        try:
            api.campaigns.post(
                Campaign(
                    name=campaign["name"],
                    groups=[Group(name=campaign["group_name"])],
                    page=Page(name=campaign["page_name"]),
                    template=new_template,
                    smtp=new_smtp,
                    url=campaign["url"],
                    launch_date=campaign["launch_date"],
                    completed_date=campaign["complete_date"],
                )
            )
        except Exception as e:
            logging.error(e)
            raise

        logging.info("Campaign %s successfully loaded.\n", campaign["name"])


def main() -> None:
    """Set up logging, connect to API, import all assessment data."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s: %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            '"%s" is not a valid logging level.  Possible values are debug, info, warning, and error.',
            log_level,
        )
        sys.exit(1)

    try:
        api = connect_api(args["API_KEY"], args["SERVER"])
        logging.debug("Connected to: %s", args["SERVER"])
    except Exception as e:
        logging.critical(e.args[0])
        # Stop logging and clean up
        logging.shutdown()
        sys.exit(1)

    # Load assessment JSON from file
    try:
        with open(args["ASSESSMENT_FILE"]) as json_file:
            assessment = json.load(json_file)
    except FileNotFoundError as e:
        logging.error("%s", e)
        # Stop logging and clean up
        logging.shutdown()
        sys.exit(1)
    except PermissionError as e:
        logging.error("%s", e)
        # Stop logging and clean up
        logging.shutdown()
        sys.exit(1)

    try:
        # Load Landing page
        assessment["pages"] = load_landings(api, assessment)

        # Load Groups into GoPhish, returns group numbers correlated to Group number
        assessment["groups"] = load_groups(api, assessment)

        # Load Campaigns
        build_campaigns(api, assessment)

        # Stop logging and clean up
        logging.shutdown()

    except Exception as e:
        logging.debug("%s: %s", type(e), e)
        logging.critical("Closing with an error. Assessment not successfully loaded.\n")
        # Stop logging and clean up
        logging.shutdown()
        sys.exit(1)
