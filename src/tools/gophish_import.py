#!/usr/bin/env python3
"""GoPhish import loads a JSON File containing a full assessment into GoPhish.

Usage:
  gophish-import [--log-level=LEVEL] [--Debug] [--reschedule] ASSESSMENT_ID SERVER API_KEY
  gophish-import (-h | --help)
  gophish-import --version

Options:
  ASSESSMENT_ID  --> Assessment ID
  SERVER         --> Full URL to GoPhish server
  API_KEY        --> API Access Key
  -h --help      Show this screen.
  --version      Show version.
  -r --reschedule     Imports a rescheduled campaign.
  -D --Debug     Enters users into pdb.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import json
import logging
import pdb

# Third-Party Libraries
from docopt import docopt
import requests
from gophish.models import *

# Inter-project
from tools.connect import connect_api

args = docopt(__doc__, version="v0.0")

# Suppress Insecure Request waring.
requests.packages.urllib3.disable_warnings()


def load_landings(api, assessment):
    pages = assessment["pages"]

    for page in pages:
        new_page = Page()
        new_page.name = page["name"]
        new_page.capture_credentials = page["capture_credentials"]
        new_page.capture_passwords = page["capture_passwords"]
        new_page.html = page["html"]
        if page["redirect_url"]:
            new_page.redirect_url = page["redirect_url"]

        # Debug page information
        logging.debug("Page Name: {}".format(new_page.name))
        logging.debug("Redirect ULR: {}".format(new_page.redirect_url))
        logging.debug("Capture Credentials: {}".format(new_page.capture_credentials))
        logging.debug("Capture Passwords: {}".format(new_page.capture_passwords))

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
                    logging.warning(f"{e}. Finding with previously loaded page.")
                    old_pages = api.pages.get()
                    for old_page in old_pages:
                        if old_page.name == new_page.name:
                            logging.debug(f"Deleting Page with ID {old_page.id}")
                            api.pages.delete(old_page.id)
                            logging.info("Re-Loading new page.")
                else:
                    logging.error(f"{e}\n")
                    raise

        # Returns Landing Page ID
        logging.info(f"Landing Page {new_page.name} loaded.\n")
        page["id"] = new_page.id

    return pages


def load_groups(api, assessment):
    groups = assessment["groups"]

    for group in groups:
        logging.info(f"Loading Group {group['name']}")

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
                    logging.warning(f"{e}. Finding previously loaded group to delete.")
                    groups = api.groups.get()
                    logging.debug(
                        f"Checking {len(groups)} for previously imported group to get ID"
                    )
                    for old_group in groups:
                        if old_group.name == new_group.name:
                            logging.debug(f"Deleting Group with ID {old_group.id}")
                            api.groups.delete(old_group.id)
                            logging.info("Re-Loading new group.")
                else:
                    logging.error(f"{e}\n")
                    raise

        group["id"] = new_group.id

        logging.info("Group Ready: {}\n".format(new_group.name))

    return groups


def build_campaigns(api, assessment):
    logging.info("Building Campaigns.")
    for campaign in assessment["campaigns"]:
        logging.info(f"Building Campaign: {campaign['name']}")

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
                        f"{e}. Finding previously loaded template to delete."
                    )
                    templates = api.templates.get()
                    logging.debug(
                        f"Checking {len(templates)} for previously imported template to get ID"
                    )
                    for old_template in templates:
                        if old_template.name == new_template.name:
                            logging.debug(
                                f"Deleting Template with ID {old_template.id}"
                            )
                            api.templates.delete(old_template.id)
                            logging.info("Re-Loading new template.")
                else:
                    logging.error(f"{e}\n")
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
                    logging.warning(f"{e}. Finding previously loaded smtp to delete.")
                    smtps = api.smtp.get()
                    logging.debug(
                        f"Checking {len(smtps)} for previously imported smtp profiles to get ID"
                    )
                    for old_smtp in smtps:
                        if old_smtp.name == new_smtp.name:
                            logging.debug(f"Deleting SMTP with ID {old_smtp.id}")
                            api.smtp.delete(old_smtp.id)
                            logging.info("Re-Loading new SMTP.")
                else:
                    logging.error(f"{e}\n")
                    raise

        # Check to remove any campaigns with the same name
        old_campaigns = api.campaigns.get()
        for old_campaign in old_campaigns:
            if old_campaign.name == campaign["name"]:
                logging.warning(
                    f"Previous Campaign found with name {campaign['name']}."
                )
                logging.warning(
                    f"Previous Campaign with id {old_campaign.id} being deleted."
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

        logging.info(f"Campaign {campaign['name']} successfully loaded.\n")


def main():
    """Drops user into pdb to set breakpoints."""
    if args["--Debug"]:
        pdb.set_trace()

    """Set up logging and call the example function."""
    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s: %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            '"{}"is not a valid logging level.  Possible values are debug, info, warning, and error.'.format(
                log_level
            )
        )
        return 1

    try:
        api = connect_api(args["API_KEY"], args["SERVER"])
        logging.debug("Connected to: {}".format(args["SERVER"]))
    except Exception as e:
        logging.critical(print(e.args[0]))
        # Stop logging and clean up
        logging.shutdown()
        return 1

    # Load assessment JSON from file
    try:
        with open(f'{args["ASSESSMENT_ID"]}.json') as json_file:
            assessment = json.load(json_file)
    except FileNotFoundError as e:
        logging.error(f"{e}\n")
        # Stop logging and clean up
        logging.shutdown()
        return 1
    except PermissionError as e:
        logging.error(f"{e}\n")
        # Stop logging and clean up
        logging.shutdown()
        return 1

    try:
        # Load Landing page
        assessment["pages"] = load_landings(api, assessment)

        # Load Groups into GoPhish, returns group numbers correlated to Group number
        assessment["groups"] = load_groups(api, assessment)

        # Load Campaigns
        build_campaigns(api, assessment)

        # Stop logging and clean up
        logging.shutdown()
        return 0

    except Exception as e:
        logging.debug(f"{type(e)}: {e}")
        logging.critical("Closing with an error. Assessment not successfully loaded.\n")
        # Stop logging and clean up
        logging.shutdown()
        return 1


if __name__ == "__main__":
    main()
