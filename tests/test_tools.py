#!/usr/bin/env pytest -vs
"""Tests for Validation functions."""

# Third-Party Libraries
import pytest

# cisagov Libraries
from tools.gophish_complete import get_campaign_id


class TestComplete:
    """Test gophish-complete script."""

    @pytest.mark.parametrize(
        "campaigns", [{"1": "RV0000-C1", "2": "RV0000-C2", "3": "RV0000-C3"}]
    )
    def test_get_campaign_id_found(self, campaigns):
        """Verify correct campaign id is returned when a valid campaign name is provided."""
        assert get_campaign_id("RV0000-C2", campaigns) == "2"

    @pytest.mark.parametrize(
        "campaigns", [{"1": "RV0000-C1", "2": "RV0000-C2", "3": "RV0000-C3"}]
    )
    def test_get_campaign_id_not_found(self, campaigns):
        """Verify LookupError is raised when searching for unknown campaign id."""
        with pytest.raises(LookupError):
            get_campaign_id("RV0000-C6", campaigns)
