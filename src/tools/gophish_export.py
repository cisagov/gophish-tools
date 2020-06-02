#!/usr/bin/env python3

"""GoPhish Export tool for a Phishing Campaign Assessment (PCA)

This tool will export an assessment into a single JSON file.

Usage:
  gophish-export [--log-level=LEVEL] ASSESSMENT_ID SERVER API_KEY
  gophish-export (-h | --help)
  gophish-export --version

Options:
  SERVER 	--> Full URL to GoPhish server
  API_KEY 	--> API Access Key
  -h --help      Show this screen.
  --version      Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""

from docopt import docopt
import requests
import httpagentparser
import sys
import hashlib
from datetime import datetime
import logging
import json

from tools.connect import connect_api


args = docopt(__doc__, version="v2.0")
# Support Insecure Request waring.


requests.packages.urllib3.disable_warnings()

# import IPython; IPython.embed() #<<< BREAKPOINT >>>
# sys.exit(0)    # Build dict of relevant campaign data


# Adds all users to the database
# STAND ALONE
def import_users(api):
    # Pulls the group IDs for any group starting with assessment ID.
    groupIDs = pull_gophish_groups(api, args["ASSESSMENT_ID"])

    users = list()

    for group_id in groupIDs:
        # Pulls target list for parsing
        targets = api.groups.get(group_id).as_dict()["targets"]

        for target in targets:

            user = dict()
            # Checks if user is in database.

            user["id"] = hashlib.sha256(target["email"].encode("utf-8")).hexdigest()
            user["customer_defined_labels"] = dict()

            if "position" in target:
                user["customer_defined_labels"][args["ASSESSMENT_ID"]] = [
                    target["position"]
                ]

            users.append(user)

        logging.info("Users for {} have been added".format(args["ASSESSMENT_ID"]))

        with open("data_" + args["ASSESSMENT_ID"] + ".json", "w") as fp:
            json.dump(users, fp, indent=4)
            fp.write(",")

    return True


# Returns a list of group IDs for all groups starting with specified assessment_id
# SUPPORTER - userControl


def pull_gophish_groups(api, assessment_id):
    rawGroup = api.groups.get()  # holds raw list of campaigns from GoPhish
    groups = list()  # Holds list of campaign IDs that match the assessment.

    for group in rawGroup:
        group = group.as_dict()
        if group["name"].startswith(assessment_id):
            groups.append(group["id"])

    return groups


# Controls the campaign importing of an assessment to DB.
# STAND ALONE
def campaignControl(api):
    campaignIDs = pull_gophish_campaign(api, args["ASSESSMENT_ID"])
    campaigns = list()

    for campaign_id in campaignIDs:
        campaigns.append(import_campaign(api, campaign_id))

    logging.info("Successfully added campaigns for {}".format(args["ASSESSMENT_ID"]))

    with open("data_" + args["ASSESSMENT_ID"] + ".json", "a") as fp:
        json.dump(campaigns, fp, indent=4)

    return True


# Returns a list of campaign IDs for all campaigns starting with specified assessment_id
# SUPPORTER - campaignControl
def pull_gophish_campaign(api, assessment_id):
    rawCampaigns = api.campaigns.get()  # holds raw list of campaigns from GoPhish
    campaigns = list()  # Holds list of campaign IDs that match the assessment.

    for campaign in rawCampaigns:
        campaign = campaign.as_dict()
        if campaign["name"].startswith(assessment_id):
            campaigns.append(campaign["id"])

    return campaigns


# Return campaign metadata for given campaign IDs
# SUPPORTER - campaignControl


def import_campaign(api, campaign_id):
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


# Returns a list of all clicks for a given campaign.
# SUPPORTER - import_campaign
def import_clicks(api, campaign_id):
    # Builds out Click
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


# Import E-mail status
# SUPPORTER - import_campaign
def get_email_status(api, campaign_id):
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
            rawEvent["time"] = datetime.strptime(
                rawEvent["time"].split(".")[0], "%Y-%m-%dT%H:%M:%S"
            )
            email["time"] = rawEvent["time"]

            email["status"] = "Failed"

        if email:
            status.append(email)

    return status


# Returns application details
# SUPPORTER - import_clicks
def get_application(rawEvent):
    application = dict()

    application["external_ip"] = rawEvent["details"]["browser"]["address"]

    # Processes user agent string.
    userAgent = rawEvent["details"]["browser"]["user-agent"]
    application["name"] = httpagentparser.detect(userAgent)["platform"]["name"]
    application["version"] = httpagentparser.detect(userAgent)["platform"]["version"]

    return application


def main():
    """Set up logging and call the example function."""
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

    # TODO Validate that requested assessment exists.

    import_users(api)
    campaignControl(api)

    logging.info("Data written to data_{}.json".format(args["ASSESSMENT_ID"]))


if __name__ == "__main__":
    main()
