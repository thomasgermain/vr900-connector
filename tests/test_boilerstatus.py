"""Tests for boiler status."""
from datetime import datetime
import unittest

from vr900connector.model import BoilerStatus


class BoilerStatusTest(unittest.TestCase):
    """Test class."""

    def test_status_error_con(self) -> None:
        """Error code 'con' means error."""
        status = BoilerStatus('Name', 'title', 'con', 'desc', datetime.now(),
                              'hint', None, None)
        self.assertTrue(status.is_error)

    def test_status_error_f(self) -> None:
        """Error code starting with F means error."""
        status = BoilerStatus('Name', 'title', 'F.28', 'desc', datetime.now(),
                              'hint', None, None)
        self.assertTrue(status.is_error)

    def test_status_no_error(self) -> None:
        """No error code."""
        status = BoilerStatus('Name', 'title', 'S.04', 'desc', datetime.now(),
                              'hint', None, None)
        self.assertFalse(status.is_error)

    def test_status_no_code(self) -> None:
        """No code available."""
        status = BoilerStatus('Name', 'title', None, 'desc', datetime.now(),
                              'hint', None, None)
        self.assertFalse(status.is_error)
