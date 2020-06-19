#!/usr/bin/env python3

"""Export all the data from an assessment within GoPhish into a single JSON file.

Usage:
  gophish-export [--log-level=LEVEL] ASSESSMENT_ID SERVER API_KEY
  gophish-export (-h | --help)
  gophish-export --version

Options:
  API_KEY                   GoPhish API key.
  ASSESSMENT_ID             ID of the assessment to export data from.
  SERVER                    Full URL to GoPhish server.
  -h --help                 Show this screen.
  --version                 Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
from datetime import datetime
import hashlib
import json
import logging
import sys
from typing import Dict

# Third-Party Libraries
from docopt import docopt
import httpagentparser
import requests

# cisagov Libraries
from tools.connect import connect_api

from ._version import __version__

# Disable "Insecure Request" warning: GoPhish uses a self-signed certificate
# as default for https connections, which can not be  verified by a third
# party; thus, an SSL insecure request warning is produced.
requests.packages.urllib3.disable_warnings()


def assessment_exists(api, assessment_id):
    """Check GoPhish has campaigns for designated assessment.

    Args:
        api (GoPhish API): Connection to GoPhish server via the API.
        assessment_id (string): Assessment identifier to get campaigns from.

    Returns:
        boolean: Indicates if a campaign is found starting with assessment_id.
    """
    allCampaigns = api.campaigns.get()
    for campaign in allCampaigns:
        if campaign.name.startswith(assessment_id):
            return True

    return False


def import_users(api, assessment_id):
    """Add all users to the database.

    Achieved by pulling the group IDs for any group starting with
    the assessment id. The targets within the group are then parsed
    into a users list of user dicts. The user dicts includes a
    sha256 hash of the target's email and  assessment id with any labels.

    Results are saved to a json file.

    Args:
        api (GoPhish API): Connection to GoPhish server via the API.
        assessment_id (string): Assessment identifier to get campaigns from.

    Returns:
        List of users from the assessment's group(s).
    """
    groupIDs = pull_gophish_groups(api, assessment_id)

    users = list()

    for group_id in groupIDs:
        # Pulls target list for parsing
        targets = api.groups.get(group_id).as_dict()["targets"]

        for target in targets:

            user = dict()

            user["id"] = hashlib.sha256(target["email"].encode("utf-8")).hexdigest()
            user["customer_defined_labels"] = dict()

            if "position" in target:
                user["customer_defined_labels"][assessment_id] = [target["position"]]

            users.append(user)

    logging.info(f"Users for {assessment_id} have been added")

    return users


def pull_gophish_groups(api, assessment_id):
    """Return a list of group IDs for all groups starting with specified assessment_id."""
    rawGroup = api.groups.get()  # holds raw list of campaigns from GoPhish
    groups = list()  # Holds list of campaign IDs that match the assessment.

    for group in rawGroup:
        group = group.as_dict()
        if group["name"].startswith(assessment_id):
            groups.append(group["id"])

    return groups


def campaignControl(api, assessment_id):
    """Control the campaign importing of an assessment to DB.

    Results are saved to a json file.

    Args:
        api (GoPhish API): Connection to GoPhish server via the API.
        assessment_id (string): Assessment identifier to get campaigns from.

    Returns:
        List of the assessment's campaigns with data.
    """
    campaignIDs = pull_gophish_campaign(api, assessment_id)
    campaigns = list()

    for campaign_id in campaignIDs:
        campaigns.append(import_campaign(api, campaign_id))

    logging.info(f"Successfully added campaigns for {assessment_id}")

    return campaigns


def pull_gophish_campaign(api, assessment_id):
    """Return a list of campaign IDs for all campaigns starting with specified assessment_id."""
    rawCampaigns = api.campaigns.get()  # holds raw list of campaigns from GoPhish
    campaigns = list()  # Holds list of campaign IDs that match the assessment.

    for campaign in rawCampaigns:
        campaign = campaign.as_dict()
        if campaign["name"].startswith(assessment_id):
            campaigns.append(campaign["id"])

    return campaigns


def import_campaign(api, campaign_id):
    """Return campaign metadata for given campaign IDs."""
    campaign = dict()

    # Pulls the campaign data as dict from database
    rawCampaign: dict = api.campaigns.get(campaign_id).as_dict()

    campaign["id"] = rawCampaign["name"]

    campaign["start_time"] = rawCampaign["launch_date"]
    campaign["end_time"] = rawCampaign["completed_date"]
    campaign["url"] = rawCampaign["url"]

    campaign["subject"] = rawCampaign["template"]["subject"]

    # Gets Template ID
    campaign["template"] = (
        api.templates.get(rawCampaign["template"]["id"]).as_dict()["name"].split("-")[2]
    )

    campaign["clicks"] = import_clicks(api, campaign_id)

    # Imports the e-mail send status.
    campaign["status"] = get_email_status(api, campaign_id)

    return campaign


def import_clicks(api, campaign_id):
    """Return a list of all clicks for a given campaign."""
    rawEvents = api.campaigns.get(campaign_id).as_dict()["timeline"]
    clicks = list()  # Holds list of all users that clicked

    for rawEvent in rawEvents:
        if rawEvent["message"] == "Clicked Link":
            click = dict()

            # Builds out click document
            click["user"] = hashlib.sha256(
                rawEvent["email"].encode("utf-8")
            ).hexdigest()
            click["source_ip"] = rawEvent["details"]["browser"]["address"]

            click["time"] = rawEvent["time"]

            click["application"] = get_application(rawEvent)
            # Adds user that clicked to a list to be returned.

            clicks.append(click)

    return clicks


def get_email_status(api, campaign_id):
    """Import email status."""
    rawEvents = api.campaigns.get(campaign_id).as_dict()["timeline"]
    status = list()
    for rawEvent in rawEvents:
        email = dict()

        if rawEvent["message"] == "Email Sent":
            email["user"] = hashlib.sha256(
                rawEvent["email"].encode("utf-8")
            ).hexdigest()

            email["time"] = rawEvent["time"]

            email["status"] = "SUCCESS"

        elif rawEvent["message"] == "Error Sending Email":

            email["user"] = hashlib.sha256(
                rawEvent["email"].encode("utf-8")
            ).hexdigest()

            # Pulls time string trimming microseconds before converting to datetime.
            # TODO Confirm this needs to happen.
            rawEvent["time"] = datetime.strptime(
                rawEvent["time"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
            email["time"] = rawEvent["time"]

            email["status"] = "Failed"

        if email:
            status.append(email)

    return status


def get_application(rawEvent):
    """Return application details."""
    application = dict()

    application["external_ip"] = rawEvent["details"]["browser"]["address"]

    # Processes user agent string.
    userAgent = rawEvent["details"]["browser"]["user-agent"]
    application["name"] = httpagentparser.detect(userAgent)["platform"]["name"]
    application["version"] = httpagentparser.detect(userAgent)["platform"]["version"]

    return application


def main():
    """Set up logging, connect to API, export all assessment data."""
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

    else:
        # Connect to API
        try:
            api = connect_api(args["API_KEY"], args["SERVER"])
            logging.debug('Connected to: {args["SERVER"]}')
        except Exception as e:
            logging.critical(print(e.args[0]))
            sys.exit(1)

    if assessment_exists(api, args["ASSESSMENT_ID"]):
        assessment_dict: Dict = dict()

        # Add users list in assessment dict.
        assessment_dict["users"] = import_users(api, args["ASSESSMENT_ID"])

        # Add campaigns list to the assessment dict.
        assessment_dict["campaigns"] = campaignControl(api, args["ASSESSMENT_ID"])

        with open(f'data_{args["ASSESSMENT_ID"]}.json', "w") as fp:
            json.dump(assessment_dict, fp, indent=4)

        logging.info(f'Data written to data_{args["ASSESSMENT_ID"]}.json')

    else:
        logging.error(
            f'Assessment "{args["ASSESSMENT_ID"]}" does not exists in GoPhish.'
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
