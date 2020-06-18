#!/usr/bin/env pytest -vs
"""Tests for Validation functions."""

# Third-Party Libraries
import mock
import pytest

# cisagov Libraries
from tools import gophish_complete, gophish_export


class TestComplete:
    """Test gophish-complete script."""

    @pytest.mark.parametrize(
        "campaigns", [{"1": "RV0000-C1", "2": "RV0000-C2", "3": "RV0000-C3"}]
    )
    def test_get_campaign_id_found(self, campaigns):
        """Verify correct campaign id is returned when a valid campaign name is provided."""
        assert gophish_complete.get_campaign_id("RV0000-C2", campaigns) == "2"

    @pytest.mark.parametrize(
        "campaigns", [{"1": "RV0000-C1", "2": "RV0000-C2", "3": "RV0000-C3"}]
    )
    def test_get_campaign_id_not_found(self, campaigns):
        """Verify LookupError is raised when searching for unknown campaign id."""
        with pytest.raises(LookupError):
            gophish_complete.get_campaign_id("RV0000-C6", campaigns)


class TestExport:
    """Test gophish-export script."""

    @mock.patch("tools.connect")
    def test_assessment_exists_found(self, mock_api, multiple_campaign_object):
        """Verify True is returned when assessment is in GoPhish."""
        mock_api.campaigns.get.return_value = multiple_campaign_object

        assert gophish_export.assessment_exists(mock_api, "RVXXX1") is True

    @mock.patch("tools.connect")
    def test_assessment_exists_not_found(self, mock_api, multiple_campaign_object):
        """Verify False is returned when assessment is not in GoPhish."""
        mock_api.campaigns.get.return_value = multiple_campaign_object

        assert gophish_export.assessment_exists(mock_api, "RVXXX3") is False
