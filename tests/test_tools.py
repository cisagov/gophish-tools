#!/usr/bin/env pytest -vs
"""Tests for Validation functions."""

# Third-Party Libraries
import pytest

# cisagov Libraries
from tools.gophish_complete import get_campaign_id


class TestComplete:
    """Test gophis-complete script."""

    @pytest.mark.parametrize(
        "campaigns", [{"1": "RV0000-C1", "2": "RV0000-C2", "3": "RV0000-C3"}]
    )
    def test_get_campaign_id_found(self, campaigns):
        """Test finding campaign id by campaign name when successful."""
        assert get_campaign_id("RV0000-C2", campaigns) == "2"

    @pytest.mark.parametrize(
        "campaigns", [{"1": "RV0000-C1", "2": "RV0000-C2", "3": "RV0000-C3"}]
    )
    def test_get_campaign_id_not_found(self, campaigns):
        """Test getting campaign id bu campaign name when unsuccessful."""
        with pytest.raises(LookupError):
            get_campaign_id("RV0000-C6", campaigns)
