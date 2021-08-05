#!/usr/bin/env python3
"""Modify campaign start/end dates in an assessment JSON file.

Usage:
  pca-assessment-reschedule [--log-level=LEVEL] ASSESSMENT_FILE
  pca-assessment-reschedule (-h | --help)
  pca-assessment-reschedule --version

Options:
  ASSESSMENT_FILE           JSON file containing the assessment information.
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

# cisagov Libraries
from models import Assessment
from util.input import get_number, get_time_input
from util.set_date import set_date

from ._version import __version__


def display_assessment_dates(assessment):
    """Display all campaigns in an assessment in a table."""
    print(f"Assessment ID: {assessment.id}")
    print(f"Start Date: {assessment.start_date}    End Date: {assessment.end_date}\n")
    print("Campaign    Launch              End")
    print("--------    ------              ---")
    for campaign in assessment.campaigns:
        print(
            f"  {campaign.name[len(campaign.name) -1 ]}        {campaign.launch_date}    {campaign.complete_date}"
        )

    print()


def change_dates(campaign, timezone):
    """Change dates for a campaign."""
    logging.info(f"Changing Dates for {campaign.name}")
    logging.debug(f"Pre-Change Launch Date: {campaign.launch_date}")
    logging.debug(f"Pre-Change Complete Date: {campaign.complete_date}")

    campaign.launch_date = get_time_input("start", timezone, campaign.launch_date)

    while True:
        campaign.complete_date = get_time_input("end", timezone, campaign.complete_date)

        if campaign.complete_date > campaign.launch_date:
            break
        else:
            logging.error("Complete Date is not after Launch Date.")

    logging.debug(f"Post-Change Launch Date: {campaign.launch_date}")
    logging.debug(f"Post-Change Complete Date: {campaign.complete_date}")

    return campaign


def reschedule(assessment):
    """Reschedule assessment dates."""
    logging.info("Determining where to start rescheduling...")
    assessment.reschedule = True
    display_assessment_dates(assessment)
    assessment.start_campaign = get_number(
        "Select a Campaign to start rescheduling at:"
    )

    for campaign in assessment.campaigns:
        if int(campaign.name[len(campaign.name) - 1]) >= assessment.start_campaign:
            campaign = change_dates(campaign, assessment.timezone)
            assessment.campaigns[assessment.start_campaign - 1] = campaign
            set_date("start_date", assessment, campaign.launch_date)
            set_date("end_date", assessment, campaign.complete_date)

    logging.info("Dates have been changed...")
    display_assessment_dates(assessment)

    return assessment


def main() -> None:
    """Set up logging and call the reschedule function."""
    args: Dict[str, str] = docopt(__doc__, version=__version__)

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
        sys.exit(1)

    try:
        with open(args["ASSESSMENT_FILE"]) as json_file:
            json_data = json.load(json_file)

    except EnvironmentError:
        logging.critical(f"JSON file not found: {args['ASSESSMENT_FILE']}")
        logging.critical("Please run command from the location with the file.")
        # Bandit complains about the input() function, but it is safe to
        # use in Python 3, which is required by this project.
        input("Press any key to close...")  # nosec

    assessment = Assessment.parse(json_data)

    assessment = reschedule(assessment)

    with open(f"{assessment.id}-reschedule.json", "w") as fp:
        json.dump(assessment.as_dict(), fp, indent=4)

    logging.info(f"Assessment JSON ready: {assessment.id}-reschedule.json")
    # Stop logging and clean up
    logging.shutdown()


if __name__ == "__main__":
    main()
