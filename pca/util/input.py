__all__ = ['yes_no_prompt', 'get_input', 'get_number', 'get_time_input']

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.completion import WordCompleter
from datetime import datetime

# Inter-Project
from pca.util.validate import *

import logging

logger = logging.getLogger(__name__)

def yes_no_prompt(message):
    return prompt('{}?(yes/no) '.format(message), completer=WordCompleter(["yes", "no"], ignore_case=True),
                  validator=BooleanValidator()).lower()

def get_input(message, default_value=""):
    return prompt(f'{message} ',default=default_value, validator=BlankInputValidator(), )


def get_number(msg):
    while True:
        try:
            num = int(get_input(msg))
            break
        except:
            logging.error("None integer entered.")
            logging.warning("Please put only an integer")
    
    return num


# Gets time from user and confirms formatting
def get_time_input(type_, time_zone, default=""):
    while True:
        try:
            input_time = get_input(
                "    Please enter the {} date and time from {} (mm/dd/YYYY HH:MM (24hr)):\n        ".format(type_, time_zone), default)
            input_time = datetime.strptime(input_time, '%m/%d/%Y %H:%M')
            break
        except ValueError as e:
            logging.error("Invalid time input: {}".format(input_time))
    
    return input_time.strftime('%m/%d/%Y %H:%M')