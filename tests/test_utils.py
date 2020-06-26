#!/usr/bin/env pytest -vs
"""Tests for GoPhish util functions."""
# Third-Party Libraries
import pytest

# cisagov Libraries
from util.utils import match_assessment_id, set_date


@pytest.mark.parametrize(
    "assessment_id,name",
    [
        ("RVXXX1", "ERXXX1-G1"),
        ("RVXXX1", "RXXX12-G1"),
        ("RVXXX1", "RXXX2-G1"),
        ("RVXXX1", "RXXX3-RXXX1-G1"),
    ],
)
def test_match_assessment_id_not_found(assessment_id, name):
    """Verify no match when not an exact match."""
    assert match_assessment_id(assessment_id, name) is False


def test_match_assessment_id_found():
    """Verify match when an exact match."""
    assert match_assessment_id("RVXXX1", "RVXXX1-G1") is True


def mock_get_group_ids(s, assessment_object):
    """Return a mock assessment object."""
    return assessment_object


@pytest.mark.parametrize(
    "type_, assessment,campaign_date",
    [
        ("start_date", mock_get_group_ids, "2020-01-20T13:00:00-05:00"),
        ("end_date", mock_get_group_ids, "2020-01-20T13:00:00-05:00"),
    ],
)
def test_set_date_blank(type_, assessment, campaign_date):
    """Validate date is set if attr is empty.

    If the assessment attribute matching type_ (start_date or end_date) is empty,
    then set that attribute to the provided campaign_date.
    """
    setattr(assessment, type_, None)

    set_date(type_, assessment, campaign_date)

    assert getattr(assessment, type_) == campaign_date


@pytest.mark.parametrize(
    "type_, assessment,campaign_date,assessment_date",
    [
        (
            "start_date",
            mock_get_group_ids,
            "2020-01-20T13:00:00-05:00",
            "2020-01-20T14:00:00-05:00",
        ),
        (
            "end_date",
            mock_get_group_ids,
            "2020-01-20T13:00:00-05:00",
            "2020-01-20T12:00:00-05:00",
        ),
    ],
)
def test_set_date_change(type_, assessment, campaign_date, assessment_date):
    """Validate if campaign date is used when appropriate.

    If the assessment attribute matching type_ (start_date or end_date) is not correct,
    then set that attribute to the provided campaign_date. For start_date, the campaign
    date is used if it is less than the assessment attr. For end_date, the campaign date
    is used if it is greater than the assessment attr.
    """
    setattr(assessment, type_, assessment_date)

    set_date(type_, assessment, campaign_date)

    assert getattr(assessment, type_) == campaign_date


@pytest.mark.parametrize(
    "type_, assessment,campaign_date,assessment_date",
    [
        (
            "start_date",
            mock_get_group_ids,
            "2020-01-20T13:00:00-05:00",
            "2020-01-20T12:00:00-05:00",
        ),
        (
            "end_date",
            mock_get_group_ids,
            "2020-01-20T13:00:00-05:00",
            "2020-01-20T14:00:00-05:00",
        ),
    ],
)
def test_set_date_no_change(type_, assessment, campaign_date, assessment_date):
    """Validate of campaign date is not used when appropriate.

    If the assessment attribute matching type_ (start_date or end_date) is correct,
    then leave attribute at the current value. For start_date, the date will be unchanged
    if the campaign date is greater than the assessment attr.  For end_date, the date
    will be unchanged if the campaign date is less than the assessment attr.
    """
    setattr(assessment, type_, assessment_date)

    set_date(type_, assessment, campaign_date)

    assert getattr(assessment, type_) == assessment_date
