"""Test for Assessment Builder."""

# Standard Python Libraries
from unittest.mock import patch

# cisagov Libraries
from assessment.builder import SELECT_MORE, set_time_zone


class TestSetTimezone:
    """Test setting timezone logic."""

    def test_radiolist_dialog_run_called(self):
        """Verify radiolist_dialog run called once."""
        with patch("assessment.builder.radiolist_dialog") as run_patch:
            set_time_zone()
            run_patch().run.assert_called_once()

    def test_select_more_option_offered(self):
        """Verify the first prompt offers a way to reach the full list."""
        with patch("assessment.builder.radiolist_dialog") as run_patch:
            set_time_zone()
            values = run_patch.call_args.kwargs["values"]
            assert values[-1][0] == SELECT_MORE
            assert all(zone.startswith("US/") for zone, _ in values[:-1])

    def test_select_more_prompts_with_every_zone(self):
        """Verify choosing "Select More" asks again with the full list."""
        with patch("assessment.builder.radiolist_dialog") as run_patch:
            run_patch.return_value.run.side_effect = [SELECT_MORE, "Asia/Tokyo"]

            assert set_time_zone() == "Asia/Tokyo"

            values = run_patch.call_args.kwargs["values"]
            assert ("Asia/Tokyo", "Asia/Tokyo") in values
            assert SELECT_MORE not in [zone for zone, _ in values]

    def test_chosen_zone_returned_without_a_second_prompt(self):
        """Verify a normal selection is returned as-is."""
        with patch("assessment.builder.radiolist_dialog") as run_patch:
            run_patch.return_value.run.return_value = "US/Eastern"

            assert set_time_zone() == "US/Eastern"
            run_patch.return_value.run.assert_called_once()
