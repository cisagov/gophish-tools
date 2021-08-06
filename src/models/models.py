"""The models library."""

# Standard Python Libraries
from datetime import datetime
from typing import Any, Dict

# TODO Research .attribute only valid properties


class Model(object):
    """The Model class."""

    _valid_properties: Dict[str, Any] = dict()

    @classmethod
    def _is_builtin(cls, obj):
        return isinstance(obj, (int, float, str, list, dict, bool))

    def as_dict(self):
        """Return a dict representation of the resource."""
        result = {}
        for key in self._valid_properties:
            val = getattr(self, key)
            if isinstance(val, datetime):
                val = val.isoformat()
            # Parse custom classes
            elif val and not Model._is_builtin(val):
                val = val.as_dict()
            # Parse lists of objects
            elif isinstance(val, list):
                # We only want to call as_dict in the case where the item
                # isn't a built in type.
                for i in range(len(val)):
                    if Model._is_builtin(val[i]):
                        continue
                    val[i] = val[i].as_dict()
            # If it's a boolean, add it regardless of the value
            elif isinstance(val, bool):
                result[key] = val

            # Add it if it's not None
            if val:
                result[key] = val
        return result

    @classmethod
    def parse(cls, json):
        """Parse a JSON object into a model instance."""
        raise NotImplementedError


class Assessment(Model):
    """The Assessment class."""

    _valid_properties: Dict[str, Any] = {
        "id": None,
        "timezone": "US/Eastern",
        "domain": None,
        "target_domains": [],
        "start_date": None,
        "end_date": None,
        "reschedule": False,
        "start_campaign": 1,
        "groups": [],
        "pages": [],
        "campaigns": [],
    }

    def __init__(self, **kwargs):
        """Create a new assessment instance."""
        for key, default in Assessment._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse assessment json."""
        assessment = cls()
        for key, val in json.items():
            if key == "campaigns":
                campaigns = [Campaign.parse(campaign) for campaign in val]
                setattr(assessment, key, campaigns)
            elif key == "page":
                setattr(assessment, key, Page.parse(val))
            elif key == "groups":
                groups = [Group.parse(group) for group in val]
                setattr(assessment, key, groups)
            elif key in cls._valid_properties:
                setattr(assessment, key, val)
        return assessment


class Page(Model):
    """The Page class."""

    _valid_properties = {
        "name": None,
        "capture_credentials": None,
        "capture_passwords": False,
        "html": None,
        "redirect_url": None,
    }

    def __init__(self, **kwargs):
        """Create a new page instance."""
        for key, default in Page._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse page json."""
        page = cls()
        for key, val in json.items():
            if key in cls._valid_properties:
                setattr(page, key, val)
        return page


class Group(Model):
    """The Group class."""

    _valid_properties: Dict[str, Any] = {"name": None, "targets": []}

    def __init__(self, **kwargs):
        """Create a new group instance."""
        for key, default in Group._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse group json."""
        group = cls()
        for key, val in json.items():
            if key == "targets":
                emails = [Target.parse(email) for email in val]
                setattr(group, key, emails)
            elif key in cls._valid_properties:
                setattr(group, key, val)
        return group


class Target(Model):
    """The Target class."""

    _valid_properties = {
        "first_name": None,
        "last_name": None,
        "email": None,
        "position": None,
    }

    def __init__(self, first_name, last_name, email, **kwargs):
        """Create a new target instance."""
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        if "position" in kwargs.keys():
            setattr(self, "position", kwargs["position"])

    @classmethod
    def parse(cls, json):
        """Parse target json."""
        email = cls(json["first_name"], json["last_name"], json["email"])
        if json["position"]:
            setattr(email, "position", json["position"])
        return email


class Template(Model):
    """The Template class."""

    _valid_properties = {
        "name": None,
        "subject": None,
        "html": None,
        "text": None,
    }

    def __init__(self, **kwargs):
        """Create a new template instance."""
        for key, default in Template._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse template json."""
        template = cls()
        for key, val in json.items():
            if key in cls._valid_properties:
                setattr(template, key, val)
        return template


class SMTP(Model):
    """The SMTP class."""

    _valid_properties = {
        "name": None,
        "from_address": None,
        "password": None,
        "host": "postfix:587",
        "interface_type": "SMTP",
        "ignore_cert": True,
    }

    def __init__(self, **kwargs):
        """Create a new SMTP instance."""
        for key, default in SMTP._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse SMTP json."""
        smtp = cls()
        for key, val in json.items():
            if key in cls._valid_properties:
                setattr(smtp, key, val)
        return smtp


class Campaign(Model):
    """The Campaign class."""

    _valid_properties = {
        "name": None,
        "launch_date": None,
        "complete_date": None,
        "url": None,
        "template": None,
        "smtp": None,
        "group_name": None,
        "page_name": None,
    }

    def __init__(self, **kwargs):
        """Create a new campaign instance."""
        for key, default in Campaign._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse campaign json."""
        campaign = cls()
        for key, val in json.items():
            if key == "template":
                template = Template.parse(val)
                setattr(campaign, key, template)
            elif key == "smtp":
                smtp = SMTP.parse(val)
                setattr(campaign, key, smtp)
            elif key in cls._valid_properties:
                setattr(campaign, key, val)
        return campaign


class Click(Model):
    """The Click class represents a Click object generated by the Gophish API when a user clicks on an email."""

    _valid_properties = {
        "message": None,
        "user": None,
        "source_ip": None,
        "time": None,
        "application": None,
    }

    def __init__(self, **kwargs):
        """Create a new click instance."""
        for key, default in Click._valid_properties.items():
            setattr(self, key, kwargs.get(key, default))

    @classmethod
    def parse(cls, json):
        """Parse click json."""
        click = cls()
        for key, val in json.items():
            if key in cls._valid_properties:
                setattr(click, key, val)

    def __getitem__(self, item):
        """Get item by attribute name."""
        return getattr(self, item)
