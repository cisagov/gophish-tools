#!/usr/bin/env python3
"""Create an assessment JSON file.

Usage:
  pca-wizard [--log-level=LEVEL] ASSESSMENT_ID
  pca-wizard (-h | --help)
  pca-wizard --version

Options:
  ASSESSMENT_ID             ID of the assessment to create a JSON file for.
  -h --help                 Show this message.
  --version                 Show version.
  -l --log-level=LEVEL      If specified, then the log level will be set to
                            the specified value.  Valid values are "debug", "info",
                            "warning", "error", and "critical". [default: info]
"""
# Standard Python Libraries
import copy
import csv
import json
import logging
from typing import Dict

# Third-Party Libraries
from docopt import docopt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import message_dialog, radiolist_dialog
import pytz

# cisagov Libraries
from models.models import (
    SMTP,
    Assessment,
    Campaign,
    Group,
    Page,
    Target,
    Template,
)
from util.input import get_input, get_number, get_time_input, yes_no_prompt
from util.set_date import set_date
from util.validate import (
    BlankInputValidator,
    EmailValidator,
    MissingKey,
    email_import_validation,
    validate_domain,
    validate_email,
)

from ._version import __version__

AUTO_FORWARD = """
                <html>
                    <body onload=\"document.forms[\'auto_forward\'].submit()\">
                        <form action=\"\" method=\"POST\" name=\"auto_forward\"> </form>
                </html>
               """


def set_time_zone():
    """Select a timezone from a list of US-based time zones.

    :return: Time zone name based on pytz.
    """
    # TODO Allow for a select more option to get access to full list of Time Zones

    # Creates list of US Time Zones
    time_zone = list()
    for zone in pytz.common_timezones:
        if zone.startswith("US/"):
            time_zone.append((zone, zone))

    # Ask user to select time zone from list.
    return radiolist_dialog(
        values=time_zone, title="Time Zone", text="Please select assessment time zone:"
    )


def display_list_groups(assessment):
    """List groups in an assessment."""
    print("\tID\tName")
    print("\t-- \t-----")

    # Prints groups or No Groups message
    if assessment.groups:
        for index, temp_group in enumerate(assessment.groups):
            print("\t{}\t{}".format(index + 1, temp_group.name))
    else:
        print("\t--NO GROUPS--")

    print("\n")


def display_list_pages(assessment):
    """List pages in an assessment."""
    print("\tID\tName")
    print("\t-- \t-----")

    # Prints pages or No pages message
    if assessment.pages:
        for index, temp_page in enumerate(assessment.pages):
            print("\t{}\t{}".format(index + 1, temp_page.name))
    else:
        print("\t--NO PAGES--")

    print("\n")


def build_assessment(assessment_id):
    """Walk user through building a new assessment document.

    :return an assessment object
    """
    logging.info("Building assessment.")
    # Initializes assessment object with ID and timezone
    assessment = Assessment(id=assessment_id, timezone=set_time_zone())

    # Uses prompt to set Assessment and target domains while not allowing blank input
    assessment.domain = get_input("    Assessment domain (subdomain.domain.tld):")
    assessment.target_domains = (
        get_input("    Targeted domain(s) separated by spaces:").lower().split(" ")
    )

    # Uses functions to build out aspects of assessment.
    assessment.pages = build_pages(assessment.id)
    assessment.groups = build_groups(assessment.id, assessment.target_domains)

    template_smtp = SMTP()
    template_smtp.name = assessment.id + "-SP"

    # Sets up smtp host info to be pre-populated.
    template_smtp.host = prompt(
        "Enter SMTP host: ", default=template_smtp.host, validator=BlankInputValidator()
    )

    # Bandit complains about the input() function, but it is safe to
    # use in Python 3, which is required by this project.
    template_smtp.username = input("SMTP User: ")  # nosec
    template_smtp.password = input("SMTP Password: ")  # nosec

    assessment.campaigns = list()
    logging.info("Building Campaigns")
    num_campaigns = get_number("    How many campaigns?")
    for campaign_number in range(0, num_campaigns):
        campaign_data = build_campaigns(assessment, campaign_number + 1, template_smtp)
        assessment.campaigns.append(campaign_data)

        set_date("start_date", assessment, campaign_data.launch_date)
        set_date("end_date", assessment, campaign_data.complete_date)

    return assessment


def build_campaigns(assessment, campaign_number, template_smtp):
    """Build a single campaign.

    Args:
        assessment (Assessment): Assessment object.
        campaign_number (int): Campaign number show position in assessment.
        template_smtp (SMTP): SMTP object holding items that are the same throughout the assessment.

    Returns:
        Campaign: A single campaign object.
    """
    # Set up component holders
    logging.info(f"Building campaign {assessment.id}-C{campaign_number}")
    campaign = Campaign(name=f"{assessment.id}-C{campaign_number}")
    # Get Launch Time
    campaign.launch_date = get_time_input("start", assessment.timezone)

    while True:
        campaign.complete_date = get_time_input("end", assessment.timezone)

        if campaign.complete_date > campaign.launch_date:
            break
        else:
            logging.error("End date is not after launch date.")

    campaign.smtp, campaign.template = import_email(
        assessment, campaign_number, template_smtp
    )

    # Select Group:
    campaign.group_name = select_group(assessment)

    # Select page:
    campaign.page_name = select_page(assessment)

    campaign.url = prompt(
        "    Campaign URL: ",
        default=f"http://{assessment.domain}",
        validator=BlankInputValidator(),
    )

    campaign = review_campaign(assessment, campaign)

    logging.info(f"Successfully added campaign {campaign.name}")

    return campaign


def review_campaign(assessment, campaign):
    """Review a campaign.

    Args:
        assessment (Assessment): Assessment object the campaign belongs to.
        campaign (Campaign): Campaign object being reviewed.

    Returns:
        Campaign: Campaign object after any needed changes.
    """
    # TODO Review group name and page name.
    while True:
        campaign_dict = campaign.as_dict()
        print("\n")

        # Outputs relevent fields except Email Template.
        for field, value in campaign_dict.items():
            if field in [
                "launch_date",
                "complete_date",
                "url",
                "name",
                "group_name",
                "page_name",
            ]:
                print(f'{field.replace("_", " ").title()}: {value}')
            elif field == "smtp":
                print("SMTP: ")
                for smtp_key, smtp_value in campaign_dict["smtp"].items():
                    print(f'\t{smtp_key.replace("_", " ").title()}: {smtp_value}')

        campaign_keys = list(campaign_dict.keys())
        campaign_keys.remove("template")

        if yes_no_prompt("\nChanges Required") == "yes":
            completer = WordCompleter(campaign_keys, ignore_case=True)
            # Loops to get valid Field name form user.
            while True:
                update_key = prompt(
                    "Which Field: ",
                    completer=completer,
                    validator=BlankInputValidator(),
                ).lower()

                if update_key == "group_name":
                    campaign.group_name = select_group(assessment)
                    break
                elif update_key == "page_name":
                    campaign.page_name = select_page(assessment)
                    break
                elif update_key == "smtp":
                    # Builds a word completion list with each word of the option being capitalized.
                    sub_completer = WordCompleter(
                        list(campaign_dict["smtp"].keys()), ignore_case=True,
                    )
                    update_sub = prompt(
                        "Which SMTP field: ",
                        completer=sub_completer,
                        validator=BlankInputValidator(),
                    ).lower()
                    try:
                        update_value = prompt(
                            f"{update_sub}: ",
                            default=campaign_dict["smtp"][update_sub],
                            validator=BlankInputValidator(),
                        )
                    except KeyError:
                        logging.error("Incorrect Field!")
                    else:
                        setattr(campaign.smtp, update_sub, update_value)
                        break
                else:
                    try:
                        update_value = prompt(
                            f"{update_key}: ",
                            default=campaign_dict[update_key],
                            validator=BlankInputValidator(),
                        )
                    except KeyError:
                        logging.error("Incorrect Field!")
                    else:
                        setattr(campaign, update_key, update_value)
                        break

        else:
            break

    return campaign


def select_group(assessment):
    """Select a group from the assessment.

    Args:
        assessment (Assessment): Assessment object.

    Returns:
        string: Name of the chosen group.
    """
    # Select Group:
    if len(assessment.groups) == 1:  # If only one auto sets.
        logging.info(f"Group auto set to {assessment.groups[0].name}")
        group_name = assessment.groups[0].name
    else:  # Allows user to choose from multiple groups;
        while True:
            try:
                display_list_groups(assessment)
                group_name = assessment.groups[
                    get_number("    Select group ID for this campaign?") - 1
                ].name
                break
            except IndexError:
                logging.error("ERROR: Invalid selection, try again.")

    return group_name


def select_page(assessment):
    """Select a page from the assessment.

    Args:
        assessment (Assessment): Assessment object.

    Returns:
        string: Name of the chosen page.
    """
    if len(assessment.pages) == 1:  # If only one auto sets.
        logging.info(f"Page auto set to {assessment.pages[0].name}")
        page_name = assessment.pages[0].name
    else:  # Allows user to choose from multiple pages
        while True:
            try:
                print("\n")
                display_list_pages(assessment)
                page_name = assessment.pages[
                    get_number("    Select the page ID for this campaign?") - 1
                ].name
                break
            except IndexError:
                logging.error("ERROR: Invalid selection, try again.")

    return page_name


def import_email(assessment, campaign_number, template_smtp):
    """Import email from file."""
    temp_template = Template(name=f"{assessment.id}-T{str(campaign_number)}")
    temp_smtp = copy.deepcopy(template_smtp)
    temp_smtp.name = f"{assessment.id}-SP-{campaign_number}"

    # Receives the file name and checks if it exists.
    while True:
        try:
            import_file_name = get_input("    Import File name?")
            # Drops .json if included so it can always be added as fail safe.
            import_file_name = import_file_name.split(".", 1)[0]

            with open(import_file_name + ".json") as importFile:
                import_temp = json.load(importFile)

            # Validates that all fields are present or raise MissingKey Error.
            email_import_validation(import_temp)
            break
        except EnvironmentError:
            logging.critical("Import File not found: {}.json".format(import_file_name))
            print("Please try again...")

        except MissingKey as e:
            # Logs and indicates the user should correct before clicking ok which will re-run the import.
            logging.critical("Missing Field from import: {}".format(e.key))
            message_dialog(
                title="Missing Field",
                text=f'Email import is missing the "{e.key}" field, please correct before clicking Ok.\n {e.key}: {e.description}',
            )

            continue

    # Finalize SMTP profile, push to GoPhish for check.
    # TODO Need to valid this formatting.
    temp_smtp.from_address = import_temp["from_address"]

    # Load
    temp_template.subject = import_temp["subject"]
    temp_template.html = import_temp["html"]
    temp_template.text = import_temp["text"]
    temp_template.name = f"{assessment.id}-T{str(campaign_number)}-{import_temp['id']}"

    return temp_smtp, temp_template


def create_email(assessment, campaign_number=""):
    """Create email."""
    temp_template = Template(name=assessment.id + "-T" + str(campaign_number))
    temp_smtp = SMTP(name=f"{assessment.id}-SP-{campaign_number}")

    # Receives the file name and checks if it exists.
    while True:
        try:
            html_file_name = get_input("HTML Template File name:")
            # Drops .html if included so it can always be added as fail safe.
            html_file_name = html_file_name.split(".", 1)[0]

            with open(html_file_name + ".html") as htmlFile:
                temp_template.html = htmlFile.read()

            break
        except EnvironmentError:
            logging.error(f"HTML Template File not found: {html_file_name}.html")
            print("Please try again...")

        # Receives the file name and checks if it exists.
    while True:
        try:
            text_file_name = get_input("    Text Template File name:")
            # Drops .txt if included so it can always be added as fail safe.
            text_file_name = text_file_name.split(".", 1)[0]

            with open(text_file_name + ".txt") as textFile:
                temp_template.text = textFile.read()

            break
        except EnvironmentError:
            logging.critical(
                "Text Template File not found: {}.txt".format(text_file_name)
            )
            print("Please try again...")

    return temp_smtp, temp_template


def build_groups(id, target_domains):
    """Build groups."""
    logging.info("Getting Group Metadata")
    groups = list()

    # Looks through to get the number of groups as a number with error checking
    num_groups = get_number("    How many groups do you need?")

    if num_groups > 1:
        logging.warning("NOTE: Please load each group as a different CSV")

    labels = yes_no_prompt("    Are there customer labels?")

    for group_num in range(int(num_groups)):
        logging.info(f"Building Group {group_num + 1}")

        new_group = Group(name=f"{id}-G{str(group_num + 1)}")

        new_group.targets = build_emails(target_domains, labels)

        logging.info(f"Group Ready: {new_group.name}")
        groups.append(new_group)

    return groups


def build_emails(domains, labels):
    """Build emails."""
    # Holds list of Users to be added to group.
    targets = list()
    domain_miss_match = list()
    format_error = list()

    # Receives the file name and checks if it exists.
    while True:
        try:
            email_file_name = get_input("    E-mail CSV name:")
            # Drops .csv if included so it can always be added as fail safe.
            email_file_name = email_file_name.split(".", 1)[0]

            with open(email_file_name + ".csv") as csv_file:
                read_csv = csv.reader(csv_file, delimiter=",")
                next(read_csv)

                for row in read_csv:
                    # Checks e-mail format, if false prints message.
                    if not validate_email(row[2]):
                        format_error.append(row)
                    # Checks that the domain matches, if false prints message,
                    elif not validate_domain(row[2], domains):
                        domain_miss_match.append(row)

                    else:
                        target = Target(
                            first_name=row[0], last_name=row[1], email=row[2]
                        )
                        target = target_add_label(labels, row, target)
                        targets.append(target)

                # Works through emails found to include formatting errors.
                print("\n")
                if len(format_error) < 2:
                    for email in format_error:
                        email[2] = prompt(
                            "Correct Email Formatting: ",
                            default=email[2],
                            validator=EmailValidator(),
                        )
                        if not validate_domain(email[2], domains):
                            domain_miss_match.append(email)
                        else:
                            target = Target(
                                first_name=email[0], last_name=email[1], email=email[2]
                            )
                            target = target_add_label(labels, email, target)
                            targets.append(target)
                else:
                    logging.error("{} Formatting Errors".format(len(format_error)))
                    if yes_no_prompt("Would you like to correct each here") == "yes":
                        for email in format_error:
                            email[2] = prompt(
                                "Correct Email Formatting: ",
                                default=email[2],
                                validator=EmailValidator(),
                            )
                            if not validate_domain(email[2], domains):
                                domain_miss_match.append(email)
                            else:
                                target = Target(
                                    first_name=row[0], last_name=row[1], email=row[2]
                                )
                                target = target_add_label(labels, email, target)
                                targets.append(target)
                    else:
                        logging.warning(
                            "Incorrectly formatted Emails will not be added, continuing..."
                        )

                # Works through emails found to have domain miss match.
                if len(domain_miss_match) < 2:
                    for email in domain_miss_match:
                        email[2] = prompt(
                            "Correct Email Domain: ",
                            default=email[2],
                            validator=EmailValidator(),
                        )
                else:
                    logging.error(
                        "{} Domain Miss Match Errors".format(len(format_error))
                    )
                    if yes_no_prompt("Would you like to correct each here") == "yes":
                        for email in domain_miss_match:
                            while True:
                                email[2] = prompt(
                                    "Correct Email Domain: ",
                                    default=email[2],
                                    validator=EmailValidator(),
                                )
                                if validate_domain(email[2], domains):
                                    target = Target(
                                        first_name=row[0],
                                        last_name=row[1],
                                        email=row[2],
                                    )
                                    target = target_add_label(labels, email, target)
                                    targets.append(target)
                                    break
                    else:
                        logging.warning(
                            "Incorrectly formatted Emails will not be added, continuing..."
                        )

            if len(targets) == 0:
                raise Exception("No targets loaded")
            break
        except EnvironmentError:
            logging.critical("Email File not found: {}.csv".format(email_file_name))
            print("\t Please try again...")
        except Exception:
            # Logs and indicates the user should correct before clicking ok which will re-run the import.
            logging.critical("No targets loaded")
            message_dialog(
                title="Missing Targets",
                text="No targets loaded from file, please check file before clicking Ok.",
            )
            continue

    return targets


def target_add_label(labels, email, target):
    """Add a label to a target."""
    if labels == "yes" and not email[3]:
        logging.error("Missing Label for {}".format(target.email))
        target.position = get_input("Please enter a label:")
    else:
        target.position = email[3]
    return target


def build_pages(id_):
    """Walk user through building multiple new page documents.

    :return a page object
    """
    pages = list()
    logging.info("Getting page metadata.")

    # Looks through to get the number of pages as a number with error checking
    num_pages = get_number("    How many pages do you need")

    for page_num in range(int(num_pages)):
        logging.info(f"Building Page {page_num + 1}")
        temp_page = Page()
        name = get_input("    Page name:")
        auto_forward = yes_no_prompt("    Will this page auto forward")

        if auto_forward == "yes":

            setattr(temp_page, "name", f"{id_}-{page_num+1}-{name}")
            temp_page.capture_credentials = True
            temp_page.capture_passwords = False
            temp_page.html = AUTO_FORWARD
            temp_page.redirect_url = get_input("    URL to forward to:")

        else:
            temp_page.name = f"{id_}-{page_num+1}-{name}"

            forward = yes_no_prompt("    Will this page forward after action")
            if forward == "yes":
                temp_page.capture_credentials = True
                temp_page.redirect_url = get_input("    URL to forward to:")
            else:
                temp_page.capture_credentials = False

            temp_page.capture_passwords = False

            # Receives the file name and checks if it exists.
            while True:
                try:
                    landing_file_name = get_input("Landing page html file name:")

                    with open(landing_file_name, "r") as landingFile:
                        temp_page.html = landingFile.read()

                    break
                except EnvironmentError:
                    logging.critical(
                        f"ERROR- Landing page file not found: {landing_file_name}"
                    )
                    print("Please try again...")

        # Debug page information
        logging.debug(f"Page Name: {temp_page.name}")
        logging.debug(f"Redirect ULR: {temp_page.redirect_url}")
        logging.debug(f"Capture Credentials: {temp_page.capture_credentials}")
        logging.debug(f"Capture Passwords: {temp_page.capture_passwords}")

        temp_page = review_page(temp_page)
        pages.append(temp_page)

    return pages


def review_page(page):
    """Review a page object."""
    # Loops until not changes are required.
    while True:
        print("\n")
        page_keys = list()
        for key, value in page.as_dict().items():
            if key != "html":
                print(f"{key}: {value}")
                page_keys.append(key)
        if yes_no_prompt("Changes required") == "yes":
            completer = WordCompleter(page_keys, ignore_case=True)

            # Loops to get a valid field name from user.
            while True:
                update_key = prompt(
                    "Which field: ",
                    completer=completer,
                    validator=BlankInputValidator(),
                ).lower()

                try:
                    update_value = prompt(
                        f"{update_key}: ",
                        default=page.as_dict()[update_key],
                        validator=BlankInputValidator(),
                    )
                except KeyError:
                    logging.error(f'"{update_key}" is an incorrect field!')
                else:
                    setattr(page, update_key, update_value)
                    break
        else:
            break
    return page


def main():
    """Set up logging and call the build_assessments function."""
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

    assessment = build_assessment(args["ASSESSMENT_ID"])

    with open(f"{assessment.id}.json", "w") as fp:
        json.dump(assessment.as_dict(), fp, indent=4)

    logging.info(f"Assessment JSON ready: {assessment.id}.json")
    # Stop logging and clean up
    logging.shutdown()


if __name__ == "__main__":
    main()
