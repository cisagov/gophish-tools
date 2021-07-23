#!/usr/bin/env pytest -vs
"""Test for Assessment Builder."""
# Third-Party Libraries
from mock import patch

# cisagov Libraries
from assessment.builder import set_time_zone


class TestSetTimezone:
    """Test setting timezone logic."""

    def test_radiolist_dialog_run_called(self):
        """Verify radiolist_dialog run called once."""
        with patch("assessment.builder.radiolist_dialog") as run_patch:
            set_time_zone()
            run_patch().run.assert_called_once()
