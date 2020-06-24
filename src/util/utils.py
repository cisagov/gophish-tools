"""The set_date function."""

# Standard Python Libraries
from datetime import datetime
from re import match


def match_assessment_id(assessment_id, name):
    """Check if assessment id starts the element name.

    As long as the pca-wizard is used the element names should
    always start with the assessment id followed by a hyphen which
    will result in match. The regular expression looks for the
    assessment id to start the string and be followed immediately
    by a hypthen(-)

    Args:
        assessment_id (string): Assessment identifier to get campaigns from.
        name (string): Name of element to be checked.

    Returns:
        boolean: Indicates if match is found.
    """
    if match(rf"^{assessment_id}+[-]", name):
        return True
    else:
        return False


def set_date(type_, assessment, campaign_date):
    """Set a date for a campaign."""
    if getattr(assessment, type_):
        assessment_time = datetime.strptime(
            "".join(getattr(assessment, type_).rsplit(":", 1)), "%Y-%m-%dT%H:%M:%S%z"
        )
        campaign_time = datetime.strptime(
            "".join(campaign_date.rsplit(":", 1)), "%Y-%m-%dT%H:%M:%S%z"
        )
        if type_ == "start_date" and assessment_time > campaign_time:
            setattr(assessment, type_, campaign_date)
        elif type_ == "end_date" and assessment_time < campaign_time:
            setattr(assessment, type_, campaign_date)
    else:
        setattr(assessment, type_, campaign_date)
