#!/usr/bin/env python3

"""GoPhish Campaign Completion tool for a Phishing Campaign Assessment (PCA)

User interface to select a campaign to complete or view a summery.  If auto
flag is provided with a CAMPAIGN_ID that campaign will be completed.

Usage:
  gophish-complete (--summary | --complete | --auto=CAMPAIGN_ID) [--log-level=LEVEL] SERVER API_KEY
  gophish-complete (-h | --help)
  gophish-complete --version


Options:
  SERVER 	--> Full URL to GoPhish server
  API_KEY 	--> API Access Key
  -c --complete   Completes Campaign and shows summary
  -s --summary    Displays Campaign Summary
  -h --help      Show this screen.
  --version      Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
  -a --auto=CAMPAIGN_ID     To complete a specific campaign, pass the campaign
                            id in this flag.
"""

# import IPython; IPython.embed() #<<< BREAKPOINT >>>
# sys.exit(0)

from docopt import docopt
import sys
import requests
import logging

from tools.connect import connect_api

args = docopt(__doc__, version="v0.1")

# Support Insecure Request waring.
requests.packages.urllib3.disable_warnings()


def get_campaigns(api):
    allCampaigns = api.campaigns.get()

    while True:
        assessment_id = input("Enter Assessment ID: ")
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
    print("Please select a Campaign ID:")
    print("\tID: Name")

    for key, name in campaigns.items():
        print("\t" + str(key) + ": " + name)

    print("")

    while True:
        inputId = input("ID: ")
        if int(inputId) in campaigns:
            break
        else:
            logging.warning("Bad Campaign ID")
            print("Try again...")

    return inputId


def complete_campaign(api, workingID):
    url = (
        args["SERVER"]
        + "/api/campaigns/"
        + workingID
        + "/complete?api_key="
        + args["API_KEY"]
    )

    response = requests.get(url=url, verify=False)

    print("\n" + response.json()["message"])

    print_summary(api, workingID)

    return True


def print_summary(api, workingID):
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

    if args["--complete"]:
        campaigns = get_campaigns(api)
        workingID = select_campaigns(campaigns)
        success = complete_campaign(api, workingID)

    elif args["--summary"]:
        campaigns = get_campaigns(api)
        workingID = select_campaigns(campaigns)
        success = print_summary(api, workingID)

    elif args["--auto"]:
        success = complete_campaign(api, args["--auto"])

    if not success:
        sys.exit(-1)


if __name__ == "__main__":
    main()
