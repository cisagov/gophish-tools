#!/usr/bin/env python3
"""PCA Assessment Reschedule to adjust scheduling in the PCA JSON File

Usage:
  pca-reschedule [--log-level=LEVEL] [--Debug] ASSESSMENT_ID
  pca-reschedule (-h | --help)
  pca-reschedule --version

Options:
  ASSESSMENT_ID     --> Assessment ID
  -h --help      Show this screen.
  --version      Show version.
  -D --Debug     Enters users into pdb. 
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""
# Standard Python Libraries
import logging
import json
import pdb

# Third-Party Libraries
from docopt import docopt

# Inter-project
from pca_assessment.models import *
from pca_assessment.util.input import *
from pca_assessment.util.set_date import set_date

args = docopt(__doc__, version='v0.0')

def display_assessment_dates(assessment):
  """Displays all campaigns in an assessment in a table"""

  print(f"Assessment ID: {assessment.id}")
  print(f"Start Date: {assessment.start_date}    End Date: {assessment.end_date}\n")
  print(f"Campaign    Launch              End")
  print(f"--------    ------              ---")
  for campaign in assessment.campaigns:
    print(f"  {campaign.name[len(campaign.name) -1 ]}        {campaign.launch_date}    {campaign.complete_date}")

  print()

def change_dates(campaign, timezone):
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
  logging.info("Determining where to start rescheduling...")
  assessment.reschedule = True
  display_assessment_dates(assessment)
  assessment.start_campaign = get_number("Select a Campaign to start rescheduling at:")

  for campaign in assessment.campaigns:
    if int(campaign.name[len(campaign.name) -1 ]) >= assessment.start_campaign:
      campaign = change_dates(campaign, assessment.timezone)
      assessment.campaigns[assessment.start_campaign - 1] = campaign
      set_date("start_date", assessment, campaign.launch_date)
      set_date("end_date", assessment, campaign.complete_date)

  logging.info("Dates have been changed...")
  display_assessment_dates(assessment)

  return assessment

def main():
    """Drops user into pdb to set breakpoints."""
    if args["--Debug"]:
        pdb.set_trace()

    """Set up logging and call the example function."""
    # Set up logging
    log_level = args["--log-level"]
    try:
        logging.basicConfig(
            format="\n%(levelname)s: %(message)s", level=log_level.upper()
        )
    except ValueError:
        logging.critical(
            '"{}"is not a valid logging level.  Possible values are debug, info, warning, and error.'.format(log_level)
        )
        return 1
    
    try:
      with open(f"{args['ASSESSMENT_ID']}.json") as json_file:
        json_data = json.load(json_file)
    
    except EnvironmentError:
        logging.critical(f"JSON File not found for Assessment: {args['ASSESSMENT_ID']}.html")
        logging.critical("Please run command from the location with the file.")
        input("Press any key to close...")
        
    assessment = Assessment.parse(json_data)

    assessment = reschedule(assessment)
    
    with open(f"{assessment.id}-reschedule.json", "w") as fp:
        json.dump(assessment.as_dict(), fp, indent=4)
    
    logging.info(f"Assessment JSON ready: {assessment.id}.json")
    # Stop logging and clean up
    logging.shutdown()


if __name__ == '__main__':
    main()

