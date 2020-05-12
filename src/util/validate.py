__all__ = [
    "validate_email",
    "validate_domain",
    "BlankInputValidator",
    "FormatError",
    "BooleanValidator",
    "EmailValidator",
    "email_import_validation",
    "MissingKey",
]

import re
from prompt_toolkit.validation import Validator, ValidationError

EMAIL_TEMPLATE = {
    "id": "Template ID from Database",
    "from_address": 'Full email address format "Display Name<email@domain.com>"',
    "subject": "Email Subject with GoPhish tags if desired",
    "html": "HTML Body of the email",
    "text": "Text Body of the email",
}


def validate_email(email):
    """Validate email format.

    Args:
        email (string): Email address om string format.

    Returns:
        Boolean: Indicating valid email address format.

    """
    if not bool(
        re.match(
            r"^[a-zA-Z0-9]+[a-zA-Z0-9-.+_]+@(\[?)[a-zA-Z0-9-.]+..([a-zA-Z]{2,3}|[0-9]{2,6})(]?)$",
            email,
        )
    ):
        raise FormatError(email)
    else:
        return True


# Checks that the domain matches that of the assessment.
def validate_domain(email, domains):
    if email.split("@")[1].lower() in domains:
        return True

    return False


# Validate import email json has appropriate fields.
def email_import_validation(import_temp):
    input_keys = import_temp.keys()
    dif = [
        i
        for i in list(input_keys) + list(EMAIL_TEMPLATE.keys())
        if i not in input_keys or i not in EMAIL_TEMPLATE.keys()
    ]

    for key in dif:
        if key in EMAIL_TEMPLATE.keys():
            raise MissingKey(key, EMAIL_TEMPLATE[key])


class BlankInputValidator(Validator):
    def validate(self, document):
        text = document.text

        if not text:
            raise ValidationError(message="Blank Input")


class BooleanValidator(Validator):
    def validate(self, document):
        text = document.text
        if text.lower() not in ["yes", "no"]:
            raise ValidationError(message="Invalid Yes/No response.")


class EmailValidator(Validator):
    def validate(self, document):
        email = document.text
        if not validate_email(email):
            raise ValidationError(message="Invalid Email Address")


class FormatError(Exception):
    def __init__(self, email):
        # Now for your custom code...
        self.email = email
        self.description = f"ERROR: {email} incorrect format"


class MissingKey(Exception):
    def __init__(self, key, description):
        # Now for your custom code...
        self.key = key
        self.description = description
