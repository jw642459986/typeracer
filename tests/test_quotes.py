"""Tests for the quotes module."""

import json
import unittest
from unittest.mock import patch, MagicMock
from typeracer.quotes import fetch_quote, QuoteFetchError


class TestFetchQuote(unittest.TestCase):
    """Tests for fetch_quote()."""

    @patch("typeracer.quotes.urllib.request.urlopen")
    def test_returns_quote_on_success(self, mock_urlopen):
        """fetch_quote returns the content field from a successful API response."""
        body = json.dumps({"content": "To be or not to be."}).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.return_value = body
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = fetch_quote()
        self.assertEqual(result, "To be or not to be.")

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
