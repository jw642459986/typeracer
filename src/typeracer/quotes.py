"""Collection of typing passages for the type racer game."""

import json
import ssl
import urllib.request
import urllib.error
from collections import namedtuple


API_URL = "https://api.quotable.io/random?minLength=40&maxLength=150"

Quote = namedtuple("Quote", ["content", "author"])


class QuoteFetchError(Exception):
    """Raised when a quote cannot be fetched from the API."""

    def __init__(self, reason: str = ""):
        self.reason = reason
        super().__init__(reason)


def fetch_quote() -> Quote:
    """Fetch a random quote from the Quotable API.

    Returns a Quote namedtuple with content and author fields.
    Raises QuoteFetchError if the request fails for any reason.
    Uses a short timeout so the game never hangs.
    """
    try:
        req = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
        # Try with default SSL context first
        try:
            resp = urllib.request.urlopen(req, timeout=3)
        except (ssl.SSLCertVerificationError, urllib.error.URLError):
            # Fall back to unverified SSL if certs are outdated
            # (common on macOS system Python where certs are not installed)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(
                API_URL, headers={"Accept": "application/json"}
            )
            resp = urllib.request.urlopen(req, timeout=3, context=ctx)

        data = json.loads(resp.read().decode("utf-8"))
        resp.close()
        content = data.get("content", "").strip()
        author = data.get("author", "").strip()
        if content:
            return Quote(content=content, author=author or "Unknown")
        raise QuoteFetchError("API returned an empty quote")
    except QuoteFetchError:
        raise
    except urllib.error.URLError as e:
        raise QuoteFetchError(f"Network error: {e.reason}") from e
    except OSError as e:
        raise QuoteFetchError(f"Connection failed: {e}") from e
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise QuoteFetchError(f"Invalid API response: {e}") from e
    except Exception as e:
        raise QuoteFetchError(f"Unexpected error: {e}") from e
