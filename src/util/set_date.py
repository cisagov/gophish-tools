__all__ = ["set_date"]

from datetime import datetime


def set_date(type_, assessment, campaign_date):
    if getattr(assessment, type_):
        assessment_time = datetime.strptime(
            getattr(assessment, type_), "%m/%d/%Y %H:%M"
        )
        campaign_time = datetime.strptime(campaign_date, "%m/%d/%Y %H:%M")
        if type_ == "start_date" and assessment_time > campaign_time:
            setattr(assessment, type_, campaign_date)
        elif type_ == "end_date" and assessment_time < campaign_time:
            setattr(assessment, type_, campaign_date)
    else:
        setattr(assessment, type_, campaign_date)
