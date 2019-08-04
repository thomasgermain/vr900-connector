from datetime import date, timedelta
import unittest

from vr900connector.model import HolidayMode


class HolidayModeTest(unittest.TestCase):

    def test_is_active_false(self):
        mode = HolidayMode(False, None, None, None)
        self.assertFalse(mode.is_currently_active)

    def test_is_active_active_no_dates(self):
        mode = HolidayMode(True, None, None, None)
        self.assertFalse(mode.is_currently_active)

    def test_is_active_active_not_between(self):
        today = date.today()
        start_date = today - timedelta(days=today.weekday() - 2)
        end_date = today - timedelta(days=today.weekday() - 1)
        mode = HolidayMode(True, start_date, end_date, 15)
        self.assertFalse(mode.is_currently_active)

    def test_is_active_active_between(self):
        today = date.today()
        start_date = today - timedelta(days=today.weekday() - 2)
        end_date = today + timedelta(days=today.weekday() + 5)
        mode = HolidayMode(True, start_date, end_date, 15)
        self.assertTrue(mode.is_currently_active)
