"""example is an example Python library and tool.

Divide one integer by another and log the result. Also log some information
from an environment variable and a package resource.

EXIT STATUS
    This utility exits with one of the following values:
    0   Calculation completed successfully.
    >0  An error occurred.

Usage:
  example [--log-level=LEVEL] <dividend> <divisor>
  example (-h | --help)

Options:
  -h --help            Show this message.
  --log-level=LEVEL    If specified, then the log level will be set to
                       the specified value.  Valid values are "debug", "info",
                       "warning", "error", and "critical". [default: info]
"""

# Standard Python Libraries
import logging
import os
import subprocess  # nosec
import sys

# Third-Party Libraries
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog

# from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.styles import Style

# cisagov Libraries
from assessment.builder import build_assessment

# Paths
CISA_HOME = os.environ.get("CISA_HOME", "/home/cisa")
EFS_SHARE = os.environ.get("EFS__SHARE", "/share")
PCA_OPS_PATH = os.environ.get("PCA_OPS_PATH", "/share/PCA")
PCA_DEV_PATH = os.environ.get("PCA_DEV_PATH", "/share/private")
CONFIG_FILE_PATH = os.environ.get("PCA_DEV_PATH", "/share/private/assessment_imports")
EXPORT_PATH = os.environ.get("EXPORT_PATH", "/share/PCA/exports")
TEMPLATE_PATH = os.environ.get("EXPORT_PATH", "/share/PCA/templates")

# Prompt Styling
BASE_PROMPT_STYLE = Style.from_dict(
    {
        "dialog": "bg:#2A72AD",
        "dialog frame.label": "bg:#7DB5FA #ffffff",
        "dialog.body": "bg:#7DB5FA #ffffff",
        "dialog shadow": "bg:#000000",
    }
)


# Helper Utils
def output_dir_setup():
    """Acts as placeholder."""
    # Testing outpur from various alias execution and storing output
    # as executed to avoid permission updates.
    # Setup /share subdirs and permissions for mapped volume data
    os.mkdir("/share/private", 775)
    os.mkdir("/share/private/assessment_imports", 775)
    os.mkdir("/share/PCA")
    os.mkdir("/share/PCA/exports")
    os.mkdir("/share/PCA/templates")


def run_command(command_string: str):
    """Acts as placeholder."""
    if not isinstance(run_command, str):
        raise TypeError("Expected string input")
    # process = subprocess.Popen(command_string.split(), shell=False)
    return subprocess.check_output(command_string, shell=False)  # nosec


class Assessment:
    """Assessment."""

    name: str
    campaign_id: str
    level: int
    config_file_path: str
    min_level: int = 1
    max_level: int = 6

    def __init__(self, name: str, level: int):
        """Run init logic."""
        self.name = name
        self.assessment_name_validator()

        self.level = level
        self.assessment_level_validator()

    def assessment_name_validator(self) -> str:
        """Validate Assessment_name/id input."""
        if not isinstance(self.name, str):
            raise TypeError("Expected string input")
        return self.name

    def assessment_level_validator(self) -> int:
        """Acts as placeholder."""
        """Validate level input of assessment 1-6."""
        if not isinstance(self.level, int):
            raise TypeError("Expected int input")
        if not self.min_level <= self.level <= self.max_level:
            raise ValueError("Assessment level is not with min_level and max_level")
        return self.level

    def get_data(self):
        """Get assessment data from gophish."""
        # TODO: Populate logic to get assessment data from gophish.
        pass

    def create(self):
        """Create and schedule a new assessment."""
        if not isinstance(self.name, str):
            raise TypeError("Name attribute is not str.")

        # TODO: Update the Assessment config prompts in the legacy tool.
        builder_ouput = build_assessment(self.name)
        logging.DEBUG("Assessment builder result: %s", builder_ouput)

        # Set config path string for generated from builder.
        self.config_file_path = "{root_path}/{assessment_name}".format(
            root_path=CONFIG_FILE_PATH, assessment_name=self.name
        )

        # Import config
        self.import_config()

    def import_config(self):
        """Import assessment config file created from builder logic."""
        # Type checking
        if not isinstance(self.config_file_path, str):
            raise TypeError("config_file_path attribute is not str.")

        # Using preconfigured container aliases for now until existing
        # funtions are setup to be imported and used here
        run_command(
            "gophish-import {config_file_path}".format(
                config_file_path=self.config_file_path
            )
        )
        # run_command(import_command)

    def export(self):
        """Export Assessment data."""
        if not isinstance(self.name, str):
            raise TypeError("name attribute is not str.")

        # Using preconfigured container aliases for now until existing
        # funtions are setup to be imported and used here
        export_command = "gophish-export {assessment_name}".format(
            assessment_name=self.name
        )
        run_command(export_command)

    def test(self):
        """Test scheduled Assessment in gophish."""
        if not isinstance(self.name, str):
            raise TypeError("Name attribute is not str.")

        # Using preconfigured container aliases for now until existing
        # funtions are setup to be imported and used here
        test_command = "gophish-test {assessment_name}".format(
            assessment_name=self.name
        )
        run_command(test_command)

    def complete(self):
        """Force complete scheduled campaign."""
        if not isinstance(self.name, str):
            raise TypeError("name attribute is not str.")

        # Using preconfigured container aliases for now until existing
        # funtions are setup to be imported and used here
        complete_command = "gophish-complete {assessment_name}".format(
            assessment_name=self.name
        )
        run_command(complete_command)

    def delete(self):
        """Delete Scheduled Campaign."""
        if not isinstance(self.name, str):
            raise TypeError("name attribute is not str.")

        # Using preconfigured container aliases for now until existing
        # funtions are setup to be imported and used here
        delete_command = "gophish-cleaner -a {assessment_name}".format(
            assessment_name=self.name
        )
        run_command(delete_command)


class Campaign:
    """Campaign."""

    name: str
    level: int
    status: str

    def __init__(self):
        """Acts as placeholder."""
        pass
        # self.name = self.assessment_name_validator(name
        # self.level = self.assessment_level_validator(level)

    def delete(self):
        """Acts as placeholder."""
        pass

    def get_data(self):
        """Acts as placeholder."""
        pass

    def view_all(self):
        """Acts as placeholder."""
        pass


class Template:
    """Template."""

    name: str
    description: str
    level: int
    use_type: str
    file_path: str

    def __init__(self):
        """Run init logic."""
        pass
        # self.name = self.assessment_name_validator(name
        # self.level = self.assessment_level_validator(level)

    def create_target_template(self):
        """Acts as placeholder."""
        result = run_command("pca-wizard-templates -t")
        return result

    def create_email_template(self):
        """Acts as placeholder."""
        result = run_command("pca-wizard-templates -e")
        return result


class DatabaseTranslator:
    """Meant to translate campaign export data to database for storage."""

    campaign_name: str
    campaign_clicks: int
    campaign_level: int
    campaign_assessments: list = []
    campaign_status: str
    database_output: dict = {}

    def __init__(self, gophish_export_data):
        """Acts as placeholder."""
        self.translate_gophish_data(gophish_export_data)

    def translate_gophish_data(self, source_data):
        """Acts as placeholder."""
        self.campaign_name = source_data.get("gophish_id")
        self.database_output = {
            "database_desired_field": "source_data_to_store",
        }


class PromptHandler:
    """Help organize prompt logic."""

    prompt_type: str
    style: dict = {}
    values: list = []
    options: dict = {}
    helper_text: str
    config_data: dict = {}

    def __init__(self, config_data: dict = {}):
        """Acts as placeholder."""
        if not isinstance(config_data, dict):
            raise TypeError("config_data is not dict.")
        self.prompt_config = config_data

    def title_formatter(self, title_text):
        """Acts as placeholder."""
        return HTML('<style fg="ansired">{title}</style>'.format(title=title_text))

    def open_input_dialog(self, title, helper_text, style=BASE_PROMPT_STYLE):
        """Acts as placeholder."""
        if not isinstance(title, str):
            raise TypeError("title is not str.")
        if not isinstance(helper_text, str):
            raise TypeError("helper_text is not str.")
        if not isinstance(style, Style):
            raise TypeError("style is not Style type.")

        self.prompt_type = "input_dialog"
        self.title = self.title_formatter(helper_text)
        self.style = style
        self.helper_text = helper_text

        return input_dialog(
            title=self.title,
            text=self.helper_text,
            style=self.style,
        ).run()

    def open_radio_dialog(self, title, helper_text, values, style=BASE_PROMPT_STYLE):
        """Acts as placeholder."""
        if not isinstance(title, str):
            raise TypeError("title is not str.")
        if not isinstance(helper_text, str):
            raise TypeError("helper_text is not str.")
        if not isinstance(values, list):
            raise TypeError("values is not list type.")
        if not isinstance(style, Style):
            raise TypeError("style is not Style type.")

        self.prompt_type = "radiolist_dialog"
        self.title = title
        self.helper_text = helper_text
        self.values = values
        self.style = style

        return radiolist_dialog(
            title=self.title,
            text=self.helper_text,
            values=self.values,
            style=self.style,
        ).run()


class MainApp:
    """Acts as placeholder."""

    prompt_handler = PromptHandler()

    def __init__(self, active_prompt="main_menu"):
        """Acts as placeholder."""
        self.main_menu_prompt()

    def main_menu_prompt(self):
        """Prompt for action being taken in setup."""
        menu_selection = self.prompt_handler.open_radio_dialog(
            title="LiPCA Setup",
            helper_text="Welcome to LiPCA Setup. Please select a task below: ",
            values=[
                (self.create_template_type_prompt, "Create Template"),
                (self.create_assessment, "Create Assessment"),
                (self.export_id_prompt, "Export Assessment Data"),
            ],
        )
        return menu_selection()

    def manage_templates(self):
        """Acts as placeholder."""
        menu_selection = radiolist_dialog(
            title="Li-PCA_Manage_Templates",
            text="Template Management - Please select a task: ",
            values=[
                (self.create_template, "Create New Template."),
                # TODO: add options to display and delete templates.
                # (self.view_templates, "View Existing Templates."),
                # (self.delete_template, "Delete Existing Template."),
            ],
            style=BASE_PROMPT_STYLE,
        ).run()
        return menu_selection()

    def create_assessment(self):
        """Create campaign."""
        self.assessment = Assessment(
            name=self.assessment_id_prompt(),
            level=self.assessment_level_prompt(),
        )
        self.assessment.create()

    def export_assessment(self):
        """Acts as placeholder."""
        campaign = Campaign()
        campaign.name = self.export_id_prompt()
        return campaign.export_campaign()

    def complete_campaign(self):
        """Acts as placeholder."""
        campaign = Campaign()
        campaign.name = self.assessment_id_prompt()
        return campaign.export_campaign()

    def assessment_level_prompt(self):
        """Sub Prompt for inputting level of assessment 1-6."""
        prompt_result = input_dialog(
            title=HTML('<style fg="ansired">Assessment Level Input</style>'),
            text="Please Enter a Campaign Complexity level (Integer between 1-6):",
            style=BASE_PROMPT_STYLE,
        ).run()
        return int(prompt_result)

    def assessment_id_prompt(self):
        """Sub Prompt for action being taken in setup."""
        prompt_result = input_dialog(
            title=HTML('<style fg="ansired">Assessment ID Input</style>'),
            text="Please Enter an Assessment ID:",
            style=BASE_PROMPT_STYLE,
        ).run()
        return prompt_result

    def export_id_prompt(self):
        """Sub Prompt for action being taken in setup."""
        prompt_result = input_dialog(
            title=HTML('<style fg="ansired">Export Assessment ID Input</style>'),
            text="Please Enter the Assessment ID to export:",
            style=BASE_PROMPT_STYLE,
        ).run()
        return prompt_result

    def create_template_type_prompt(self):
        """Template selection prompt."""
        template = Template()
        menu_result = radiolist_dialog(
            title="Li-PCA Template Creation",
            text="Please select the type of template you would like to create: ",
            values=[
                (template.create_target_template, "Targets Template (csv)"),
                (template.create_email_template, "Email Content Template (json)"),
            ],
            style=BASE_PROMPT_STYLE,
        ).run()
        return menu_result()

    def manage_assessments(self):
        """Manage Assessments."""
        assessment = Assessment(name="temp", level=1)
        menu_selection = radiolist_dialog(
            title="LiPCA Setup",
            text="Welcome to LiPCA Setup. Please select a setup option below: ",
            values=[
                (assessment.create, "Schedule a new Assessment."),
                (assessment.test, "Test an Existing Assessment."),
                (assessment.export, "Export Complete an Existing Assessment."),
                (assessment.complete, "Force Complete an Existing Assessment."),
                (assessment.delete, "Delete an Existing Assessment."),
            ],
            style=BASE_PROMPT_STYLE,
        ).run()
        return menu_selection()

    def manage_campaigns(self):
        """Manage Campaigns."""
        assessment = Assessment(name="temp", level=1)
        menu_selection = radiolist_dialog(
            title="LiPCA Setup",
            text="Welcome to LiPCA Setup. Please select a setup option below: ",
            values=[
                (assessment.create, "Create Campaign."),
                (assessment.export, "Export Campaign."),
                (assessment.delete, "Delete Campaign."),
            ],
            style=BASE_PROMPT_STYLE,
        ).run()
        return menu_selection()


def main() -> int:
    """Set up logging and call the example function."""
    MainApp()
    return 0


if __name__ == "__main__":
    sys.exit(main())
    ""
