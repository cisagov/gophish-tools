#!/usr/bin/env pytest -vs
"""Tests for assessment JSON."""

# cisagov Libraries
import assessment.builder as assessment_builder

# TODO Make test_emails csv


class TestPlainAssessment:
    """Plain assessment test class."""

    get_input_values = [
        ["2. Assessment Domain- 106", "bad.tld"],
        ["3. Target Domain- 108", "target.tld"],
        ["6. Redirect URL-453", "redirect.tld"],
        ["10. Email CSV- 344", "data/test_group.csv"],
        ["17. Email File 1- 237", "data/C1.json"],
        ["23. Email File 2- 237", "data/C2.json"],
        ["28. Email File 3- 237", "data/C3.json"],
        ["33. Email File 4- 237", "data/C4.json"],
        ["38. Email File 4- 237", "data/C5.json"],
        ["43. Email File 4- 237", "data/C6.json"],
    ]
    get_input = [["12. SMTP User", ""], ["13. SMTP Password", ""]]
    yes_no_values = [
        ["5. Auto Forward- 445", "yes"],
        ["7. Page Review", "no"],
        ["9. Group Labels- 320", "yes"],
        ["20. Campaign 1 Review", "no"],
        ["25. Campaign 2 Review", "no"],
        ["30. Campaign 3 Review", "no"],
        ["35. Campaign 4 Review", "no"],
        ["40. Campaign 5 Review", "no"],
        ["45. Campaign 6 Review", "no"],
    ]
    get_number_values = [
        ["4. Number of Pages", 1],
        ["8. Num Groups- 315", 1],
        ["14. Num Campaigns- 114", 6],
    ]

    get_time_input_values = [
        ["15. Campaign 1 Launch Date- 130", "2020-01-20T13:00:00-04:00"],
        ["16. Campaign 1 End Date- 133", "2020-01-20T13:30:00-04:00"],
        ["21. Campaign 2 Launch Date- 130", "2020-01-20T14:00:00-04:00"],
        ["22. Campaign 2 End Date- 133", "2020-01-20T14:30:00-04:00"],
        ["26. Campaign 3 Launch Date- 130", "2020-01-20T15:00:00-04:00"],
        ["27. Campaign 3 End Date- 133", "2020-01-20T15:30:00-04:00"],
        ["31. Campaign 4 Launch Date- 130", "2020-01-20T16:00:00-04:00"],
        ["32. Campaign 4 End Date- 133", "2020-01-20T16:30:00-04:00"],
        ["36. Campaign 5 Launch Date- 130", "2020-01-20T17:00:00-04:00"],
        ["37. Campaign 5 End Date- 133", "2020-01-20T17:30:00-04:00"],
        ["41. Campaign 6 Launch Date- 130", "2020-01-20T18:00:00-04:00"],
        ["42. Campaign 6 End Date- 133", "2020-01-20T18:30:00-04:00"],
    ]

    prompt_values = [
        ["11. SMTP Host", "postfix:587"],
        ["18. Campaign 1 Url- 152", "http://bad.domain/camp1"],
        ["24. Campaign 2 Url- 152", "http://bad.domain/camp2"],
        ["29. Campaign 3 Url- 152", "http://bad.domain/camp3"],
        ["34. Campaign 4 Url- 152", "http://bad.domain/camp4"],
        ["39. Campaign 3 Url- 152", "http://bad.domain/camp5"],
        ["44. Campaign 4 Url- 152", "http://bad.domain/camp6"],
    ]

    radio_dialog_values = [["1. Time Zone - 63", "US/Eastern"]]

    def mock_get_input(self, s):
        """Return a mock input value."""
        return self.get_input_values.pop(0)[1]

    def mock_input(self, s):
        """Return a mock input."""
        return self.get_input.pop(0)[1]

    def mock_yes_no(self, s):
        """Return a mock yes/no value."""
        return self.yes_no_values.pop(0)[1]

    def mock_get_number(self, s):
        """Return a mock number value."""
        return self.get_number_values.pop(0)[1]

    def mock_get_time_input(self, type_, timezone):
        """Return a mock time input value."""
        return self.get_time_input_values.pop(0)[1]

    def mock_prompt(self, s, validator, default):
        """Return a mock prompt value."""
        return self.prompt_values.pop(0)[1]

    def mock_radio(self, values, title, text):
        """Return a mock radio dialog value."""
        return self.radio_dialog_values.pop(0)[1]

    def mock_id_arg(self, s):
        """Return a mock assessment ID value."""
        return "RVXXX1"

    def test_assessment(self):
        """Construct a test assessment from mock data."""
        assessment_builder.get_input = self.mock_get_input
        assessment_builder.input = self.mock_input
        assessment_builder.yes_no_prompt = self.mock_yes_no
        assessment_builder.get_number = self.mock_get_number
        assessment_builder.get_time_input = self.mock_get_time_input
        assessment_builder.prompt = self.mock_prompt
        assessment_builder.radiolist_dialog = self.mock_radio
        assessment_builder.args["ASSESSMENT_ID"] = "RVXXX1"  # self.mock_id_arg

        assessment_builder.main()
        assert True
