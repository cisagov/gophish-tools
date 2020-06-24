#!/usr/bin/env pytest -vs
"""Tests for GoPhish util functions."""
# Third-Party Libraries
import pytest

# cisagov Libraries
from util.utils import match_assessment_id


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
