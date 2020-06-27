#!/usr/bin/env pytest -vs
"""Tests for builder script."""

# Standard Python Libraries
from unittest.mock import mock_open, patch

# cisagov Libraries
from assessment.builder import build_pages, review_campaign, review_page


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
