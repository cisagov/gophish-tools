#!/usr/bin/env pytest -vs
"""Tests for builder script."""

# Standard Python Libraries
from unittest.mock import mock_open, patch

# Third-Party Libraries
import pytest

# cisagov Libraries
from assessment.builder import (
    build_assessment,
    build_emails,
    build_pages,
    review_campaign,
    review_page,
    target_add_label,
)


class TestReviewCampaign:
    """Review camaping function test class."""

    @patch("assessment.builder.yes_no_prompt", return_value="no")
    def test_no_review(self, mock_yes_no, campaign_object, assessment_object):
        """Validate no changes made when review is no."""
        reviewed_object = review_campaign(assessment_object, campaign_object)

        assert reviewed_object.as_dict() == campaign_object.as_dict()

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch("assessment.builder.prompt", return_value=["url", "change"])
    def test_change_url(
        self, mock_prompt, mock_yes_no, campaign_object, assessment_object
    ):
        """Validate url successfully changes."""
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.url = "change"

        assert reviewed_object.as_dict() == campaign_object.as_dict()

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch(
        "assessment.builder.prompt",
        return_value=["launch_date", "2020-06-20T13:00:00-04:00"],
    )
    def test_change_launch_date(
        self, mock_prompt, mock_yes_no, campaign_object, assessment_object
    ):
        """Validate launch date successfully changes."""
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.launch_date = "2020-06-20T13:00:00-04:00"

        assert reviewed_object.as_dict() == campaign_object.as_dict()

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch(
        "assessment.builder.prompt",
        return_value=["completed_date", "2020-06-20T13:00:00-04:00"],
    )
    def test_change_completed_date(
        self, mock_prompt, mock_yes_no, campaign_object, assessment_object
    ):
        """Validate end date successfully changes."""
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.completed_date = "2020-06-20T13:00:00-04:00"

        assert reviewed_object.as_dict() == campaign_object.as_dict()

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch("assessment.builder.prompt", return_value="group_name")
    @patch("assessment.builder.get_number", return_value=1)
    def test_change_group_name(
        self,
        mock_get_number,
        mock_prompt,
        mock_yes_no,
        campaign_object,
        assessment_object,
        group_object,
    ):
        """Validate group name successfully changes."""
        group_object.name = "RVXXX1-G2"
        assessment_object.groups.append(group_object)
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.group_name = "RVXXX1-G2"

        assert reviewed_object.as_dict() == campaign_object.as_dict()

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch("assessment.builder.prompt", return_value="page_name")
    @patch("assessment.builder.get_number", return_value=1)
    def test_change_page_name(
        self,
        mock_get_number,
        mock_prompt,
        mock_yes_no,
        campaign_object,
        assessment_object,
        page_object,
    ):
        """Validate page name successfully changes."""
        page_object.name = "RVXXX1-2-AutoForward"
        assessment_object.pages.append(page_object)
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.page_name = "RVXXX1-2-AutoForward"

        assert reviewed_object.page_name == campaign_object.page_name

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch("assessment.builder.prompt", return_value=["smtp", "from_address", "sender"])
    def test_change_smtp_from_address(
        self, mock_prompt, mock_yes_no, campaign_object, assessment_object
    ):
        """Validate smtp from address successfully changes."""
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.smtp.from_address = "sender"

        assert reviewed_object.smtp.from_address == campaign_object.smtp.from_address

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch("assessment.builder.prompt", return_value=["smtp", "host", "server"])
    def test_change_smtp_host(
        self, mock_prompt, mock_yes_no, campaign_object, assessment_object
    ):
        """Validate smtp host successfully changes."""
        reviewed_object = review_campaign(assessment_object, campaign_object)
        campaign_object.smtp.host = "server"

        assert reviewed_object.smtp.host == campaign_object.smtp.host


class TestBuildPages:
    """Build page function test class."""

    html_content = """
        <!DOCTYPE html>
        <html>
        <body>

            <h1>A landing page</h1>
            <p>More of that page.</p>

        </body>
        </html>
        """

    @patch("assessment.builder.get_number", return_value=2)
    @patch(
        "assessment.builder.get_input",
        side_effect=[
            "404Page",
            "http://bad.tld/404",
            "CustomerPage",
            "http://bad.tld/landing",
            "landing.html",
        ],
    )
    @patch(
        "assessment.builder.yes_no_prompt",
        side_effect=["yes", "no", "no", "yes", "no"],
    )
    @patch("assessment.builder.open", mock_open(read_data=html_content))
    def test_build_page(self, mock_open, mock_yes_no, mock_get_input, page_object_list):
        """Validate build page autoforward and load page works."""
        new_pages = build_pages("RVXXX1")

        for x in range(2):
            assert new_pages[x].as_dict() == page_object_list[x].as_dict()

    @patch("assessment.builder.yes_no_prompt", return_value=["yes", "no"])
    @patch("assessment.builder.prompt", return_value=["redirect_url", "new.domain.tld"])
    def test_change_redirect_url(self, mock_prompt, mock_yes_no, page_object):
        """Validate redirect url successfully changes."""
        reviewed_object = review_page(page_object)
        page_object.redirect_url = "new.domain.tld"

        assert reviewed_object.redirect_url == page_object.redirect_url


class TestBuildAssessment:
    """Build assessment function test class."""

    @patch("assessment.builder.radiolist_dialog", return_value="US/Eastern")
    @patch(
        "assessment.builder.get_input",
        side_effect=["bad.domain", "target.1.Domain target.2.domain"],
    )
    @patch("assessment.builder.build_pages")
    @patch("assessment.builder.build_groups")
    @patch("assessment.builder.prompt", return_value="postfix:587")
    @patch("assessment.builder.input", return_value=["", ""])
    @patch("assessment.builder.get_number", return_value=1)
    @patch("assessment.builder.build_campaigns")
    def test_build_assessment(
        self,
        mock_campaign,
        mock_get_number,
        mock_input,
        mock_prompt,
        mock_group,
        mock_page,
        mock_get_input,
        mock_radio,
        assessment_object,
        campaign_object,
        group_object,
        page_object,
    ):
        """Validate build assessment returns an assessment object."""
        mock_campaign.return_value = campaign_object
        mock_group.return_value = [group_object]
        mock_page.return_value = [page_object]

        assessment_object.target_domains = ["target.1.domain", "target.2.domain"]

        new_assessment = build_assessment("RVXXX1")
        assert new_assessment.as_dict() == assessment_object.as_dict()


class TestBuildEmails:
    """Build email function test class."""

    csv_content = """First Name,Last Name,Email,Position\nJohn,Doe,john.doe@domain.test,IT\nJane,Smith,jane.smith@domain.test,HR"""

    @patch("assessment.builder.get_input", return_value="file.csv")
    @patch("assessment.builder.open", mock_open(read_data=csv_content))
    def test_build_emails_valid(self, mock_get_input, target_json):
        """Validate build emails returns an accurate target list."""
        new_target = build_emails(["domain.test"], "yes")

        for x in range(2):
            assert new_target[x].as_dict() == target_json[x]

    @pytest.mark.parametrize("position", [None, "IT"])
    @patch("assessment.builder.get_input", return_value="HR")
    def test_target_add_label(self, mock_get_input, target_object, position):
        """Validate requests a postions if blank or sets if provided."""
        new_target = target_object
        new_target.postion = position
        raw_target = {"Position": "IT"}

        new_target = target_add_label("yes", raw_target, new_target)

        assert new_target.as_dict() == target_object.as_dict()
