__all__ = ["connect_api"]

from gophish import Gophish

# Error Handling imports
from gophish.models import Error
from requests.exceptions import MissingSchema, ConnectionError


def connect_api(api_key, server):
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
        raise Exception(f"Networking Error, unable to reach GoPhish.")

    except Exception as e:
        raise Exception(f"Cannot connect to GoPhish.")
