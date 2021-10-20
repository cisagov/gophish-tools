"""Validation functions."""

# Standard Python Libraries
import re

# Third-Party Libraries
from prompt_toolkit.validation import ValidationError, Validator

EMAIL_TEMPLATE = {
    "id": "Template ID from Database",
    "from_address": 'Full email address format "Display Name<email@domain.com>"',
    "subject": "Email Subject with GoPhish tags if desired",
    "html": "HTML Body of the email",
    "text": "Text Body of the email",
}


def validate_assessment_id(assessment_id):
    """Validate that the provided assessment_id is matching the valid assessment_id format. Example: RV1234.

    Args:
        assessment_id (string): Assessment identifier to validate.

    Returns:
        match: the result of a regular expression match.
    """
    match = re.match(r"^RV\d{4}", assessment_id)

    return match


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


def validate_domain(email, domains):
    """Check that the domain matches that of the assessment."""
    if email.split("@")[1].lower() in domains:
        return True

    return False


def email_import_validation(import_temp):
    """Validate that import email JSON has appropriate fields."""
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
    """The BlankInputValidator class."""

    def validate(self, document):
        """Validate if input text is empty."""
        text = document.text

        if not text:
            raise ValidationError(message="Blank Input")


class BooleanValidator(Validator):
    """The BooleanValidator class."""

    def validate(self, document):
        """Validate if input text is 'yes' or 'no'."""
        text = document.text
        if text.lower() not in ["yes", "no"]:
            raise ValidationError(message="Invalid Yes/No response.")


class EmailValidator(Validator):
    """The EmailValidator class."""

    def validate(self, document):
        """Validate if input text is a valid email address."""
        email = document.text
        if not validate_email(email):
            raise ValidationError(message="Invalid Email Address")


class FormatError(Exception):
    """The FormatError class."""

    def __init__(self, email):
        """TBD."""
        # Now for your custom code...
        self.email = email
        self.description = f"ERROR: {email} incorrect format"


class MissingKey(Exception):
    """The MissingKey class."""

    def __init__(self, key, description):
        """TBD."""
        # Now for your custom code...
        self.key = key
        self.description = description
