"""Functions related to user input."""

# Standard Python Libraries
from datetime import datetime
import logging

# Third-Party Libraries
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
import pytz

# cisagov Libraries
from util.validate import BlankInputValidator, BooleanValidator

logger = logging.getLogger(__name__)


def yes_no_prompt(message):
    """Prompt for a yes/no response."""
    return prompt(
        "{}?(yes/no) ".format(message),
        completer=WordCompleter(["yes", "no"], ignore_case=True),
        validator=BooleanValidator(),
    ).lower()


def get_input(message, default_value=""):
    """Record user input."""
    return prompt(
        f"{message} ", default=default_value, validator=BlankInputValidator(),
    )


def get_number(msg):
    """Validate a numerical input."""
    while True:
        try:
            num = int(get_input(msg))
            break
        except ValueError:
            logging.error("None integer entered.")
            logging.warning("Please put only an integer")

    return num


# Gets time from user and confirms formatting
def get_time_input(type_, time_zone, default=""):
    """Get time input with time_zone and convert to ISO format.

    Utility for getting time input for a specific date type (start/end)
    in a specific timzone. Once received, input is validated and converted
    to ISO format.

    Arguments:
        type_ {str} -- Indiateds the date, start or complete genearly.
        time_zone {str} --  pytz timezone in a string

    Keyword Arguments:
        default {str} -- Default value to pre-populate user input (default: {""})

    Returns:
        str -- String ISO representation of provided time in UTC.
    """
    while True:
        try:
            input_time = get_input(
                "    Please enter the {} date and time from {} (mm/dd/YYYY HH:MM (24hr)):\n        ".format(
                    type_, time_zone
                ),
                default,
            )
            input_time = datetime.strptime(input_time, "%m/%d/%Y %H:%M")
            break
        except ValueError:
            logging.error("Invalid time input: {}".format(input_time))

    # Convert time to ISO format to be returned.
    return pytz.timezone(time_zone).localize(input_time).isoformat()
