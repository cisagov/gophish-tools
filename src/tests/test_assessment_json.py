import pca.assessment.builder as assessment_builder


# TODO Make test_emails csv


class TestPlainAssessment:
    get_input_values = [
        ["Assessment Domain- 106", "bad.domain"],
        ["Target Domain- 107", "target.domain"],
        ["Redirect URL-453", "redirect.domain"],
        ["Email CSV- 344", "data/test_emails.csv"],
        ["Email File- 237", "data/C1.json"],
    ]
    yes_no_values = [
        ["Auto Forward- 445", "yes"],
        ["Page Review", "no"],
        ["Group Labels- 320", "yes"],
        ["Import Email 1- 140", "yes"],
    ]
    get_number_values = [["Num Groups- 315", 1], ["Num Campaigns- 114", 1]]

    get_time_input_values = [
        ["Campaign 1 Launch Date- 130", "01/20/2020 13:00"],
        ["Campaign 1 End Date- 133", "01/20/2020 13:30"],
    ]

    prompt_values = [["Campaign 1 Url- 152", "bad.domain/camp1"]]

    radio_dialog_values = [["Time Zone", "US/Eastern"]]

    def mock_get_input(self, s):
        return self.get_input_values.pop(0)[1]

    def mock_yes_no(self, s):
        return self.yes_no_values.pop(0)[1]

    def mock_get_number(self, s):
        return self.get_number_values.pop(0)[1]

    def mock_get_time_input(self, type_, timezone):
        return self.get_time_input_values.pop(0)[1]

    def mock_prompt(self, s, default, validator):
        return self.prompt_values.pop(0)[1]

    def mock_radio(self, values, title, text):
        return self.radio_dialog_values.pop(0)[1]

    def mock_id_arg(selfs, s):
        return "RVXXX1"

    def test_assessment(self):
        assessment_builder.get_input = self.mock_get_input
        assessment_builder.yes_no_prompt = self.mock_yes_no
        assessment_builder.get_number = self.mock_get_number
        assessment_builder.get_time_input = self.mock_get_time_input
        assessment_builder.prompt = self.mock_prompt
        assessment_builder.radiolist_dialog = self.mock_radio
        assessment_builder.args["ASSESSMENT_ID"] = self.mock_id_arg

        assessment_builder.main()
        assert True
