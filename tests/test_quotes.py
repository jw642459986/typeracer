"""Tests for the quotes module."""

import json
import unittest
from unittest.mock import patch, MagicMock
from typeracer.quotes import fetch_quote, Quote, QuoteFetchError


class TestFetchQuote(unittest.TestCase):
    """Tests for fetch_quote()."""

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_returns_quote_with_author(self, mock_urlopen):
        """fetch_quote returns a Quote with content and author from the API."""
        body = json.dumps({
            "content": "To be or not to be.",
            "author": "Shakespeare",
        }).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = fetch_quote()
        self.assertIsInstance(result, Quote)
        self.assertEqual(result.content, "To be or not to be.")
        self.assertEqual(result.author, "Shakespeare")

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_missing_author_defaults_to_unknown(self, mock_urlopen):
        """fetch_quote sets author to 'Unknown' when API omits it."""
        body = json.dumps({"content": "Some wise words."}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = fetch_quote()
        self.assertEqual(result.content, "Some wise words.")
        self.assertEqual(result.author, "Unknown")

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_empty_author_defaults_to_unknown(self, mock_urlopen):
        """fetch_quote sets author to 'Unknown' when author is empty string."""
        body = json.dumps({"content": "A quote.", "author": ""}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = fetch_quote()
        self.assertEqual(result.author, "Unknown")

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_raises_on_empty_content(self, mock_urlopen):
        """fetch_quote raises QuoteFetchError when API returns empty content."""
        body = json.dumps({"content": ""}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(QuoteFetchError) as ctx:
            fetch_quote()
        self.assertIn("empty", str(ctx.exception).lower())

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_raises_on_network_error(self, mock_urlopen):
        """fetch_quote raises QuoteFetchError on network failure."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

        with self.assertRaises(QuoteFetchError) as ctx:
            fetch_quote()
        self.assertIn("Network error", str(ctx.exception))

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_raises_on_timeout(self, mock_urlopen):
        """fetch_quote raises QuoteFetchError on socket timeout."""
        import socket
        mock_urlopen.side_effect = socket.timeout("timed out")

        with self.assertRaises(QuoteFetchError) as ctx:
            fetch_quote()
        self.assertIn("Connection failed", str(ctx.exception))

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_raises_on_invalid_json(self, mock_urlopen):
        """fetch_quote raises QuoteFetchError when API returns invalid JSON."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"not json at all"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(QuoteFetchError) as ctx:
            fetch_quote()
        self.assertIn("Invalid API response", str(ctx.exception))

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_raises_on_missing_content_key(self, mock_urlopen):
        """fetch_quote raises QuoteFetchError when JSON has no content field."""
        body = json.dumps({"text": "no content key"}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        with self.assertRaises(QuoteFetchError) as ctx:
            fetch_quote()
        self.assertIn("empty", str(ctx.exception).lower())


class TestQuote(unittest.TestCase):
    """Tests for the Quote namedtuple."""

    def test_fields(self):
        q = Quote(content="Hello.", author="Someone")
        self.assertEqual(q.content, "Hello.")
        self.assertEqual(q.author, "Someone")

    def test_indexing(self):
        q = Quote(content="Hello.", author="Someone")
        self.assertEqual(q[0], "Hello.")
        self.assertEqual(q[1], "Someone")


class TestQuoteFetchError(unittest.TestCase):
    """Tests for the QuoteFetchError exception."""

    def test_stores_reason(self):
        err = QuoteFetchError("something broke")
        self.assertEqual(err.reason, "something broke")
        self.assertEqual(str(err), "something broke")

    def test_default_reason(self):
        err = QuoteFetchError()
        self.assertEqual(err.reason, "")


if __name__ == "__main__":
    unittest.main()
