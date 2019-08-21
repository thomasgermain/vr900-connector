"""Tests for boiler status."""
import datetime
import unittest

from vr900connector.model import BoilerStatus


class BoilerStatusTest(unittest.TestCase):
    """Test class."""

    def test_status_error_con(self) -> None:
        """Error code 'con' means error."""
        status = BoilerStatus('Name', 'desc', 'title', 'con', 'hint',
                              datetime.datetime.now(), None, None)
        self.assertTrue(status.is_error)

    def test_status_error_f(self) -> None:
        """Error code starting with F means error."""
        status = BoilerStatus('Name', 'desc', 'title', 'F.28', 'hint',
                              datetime.datetime.now(), None, None)
        self.assertTrue(status.is_error)

    def test_status_no_error(self) -> None:
        """No error code."""
        status = BoilerStatus('Name', 'desc', 'title', 'S.04', 'hint',
                              datetime.datetime.now(), None, None)
        self.assertFalse(status.is_error)

    def test_status_no_code(self) -> None:
        """No code available."""
        status = BoilerStatus('Name', 'desc', 'title', None, 'hint',
                              datetime.datetime.now(), None, None)
        self.assertFalse(status.is_error)
