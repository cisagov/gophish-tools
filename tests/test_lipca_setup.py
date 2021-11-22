#!/usr/bin/env pytest -vs
"""Test for Assessment Builder."""
# Third-Party Libraries
import pytest

# cisagov Libraries
from assessment.lipca_setup import run_command

# from mock import patch


class TestRunCommand:
    """Test setting timezone logic."""

    def test_run_command_no_string_fails(self):
        """Verify radiolist_dialog run called once."""
        in_val = 1
        with pytest.raises(TypeError):
            run_command(in_val)


# class TestAssessmentLevelInput:
#     """Test setting timezone logic."""
#
#     def test_radiolist_dialog_run_called(self):
#         """Verify radiolist_dialog run called once."""
#         with assert r
#         with patch("assessment.builder.radiolist_dialog") as run_patch:
#             set_time_zone()
#             run_patch().run.assert_called_once()
#
#
# class TestNameInput:
#     """Test setting timezone logic."""
#
#     def test_radiolist_dialog_run_called(self):
#         """Verify radiolist_dialog run called once."""
#         with patch("assessment.builder.radiolist_dialog") as run_patch:
#             set_time_zone()
#             run_patch().run.assert_called_once()
#
#
# class TestNameInput:
#     """Test setting timezone logic."""
#
#     def test_radiolist_dialog_run_called(self):
#         """Verify radiolist_dialog run called once."""
#         with patch("assessment.builder.radiolist_dialog") as run_patch:
#             set_time_zone()
#             run_patch().run.assert_called_once()
#
# class TestNameInput:
#     """Test setting timezone logic."""
#
#     def test_radiolist_dialog_run_called(self):
#         """Verify radiolist_dialog run called once."""
#         with patch("assessment.builder.radiolist_dialog") as run_patch:
#             set_time_zone()
#             run_patch().run.assert_called_once()
