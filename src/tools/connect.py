"""Module to create a Gophish API connection."""

# Third-Party Libraries
# No type stubs exist for gophish, so we add "type: ignore" to tell mypy to
# ignore this library
from gophish import Gophish  # type: ignore
from gophish.models import Error  # type: ignore
from requests.exceptions import ConnectionError, MissingSchema


def connect_api(api_key, server):
    """Create a Gophish API connection."""
    api = Gophish(api_key, host=server, verify=False)

    # Sets up connection and test that it works.
    try:
        api.campaigns.get()
        return api

    except Error as e:  # Bad API Key
        raise Exception(f"Error Connecting: {e.message}")
    except MissingSchema as e:
        message = e.args[0].split(" '")[0]
        raise Exception(f"Error Connecting: {message}")

    except ConnectionError:
        raise Exception("Networking Error, unable to reach Gophish.")

    except Exception:
        raise Exception("Cannot connect to Gophish.")
