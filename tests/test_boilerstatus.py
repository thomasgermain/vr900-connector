import datetime
import unittest

from vr900connector.model import BoilerStatus


class BoilerStatusTest(unittest.TestCase):

    def test_status_error_con(self):
        status = BoilerStatus('Name', 'desc', 'title', 'con', 'hint', datetime.datetime.now(), '', '')
        self.assertTrue(status.is_error)

    def test_status_error_f(self):
        status = BoilerStatus('Name', 'desc', 'title', 'F.28', 'hint', datetime.datetime.now(), '', '')
        self.assertTrue(status.is_error)

    def test_status_no_error(self):
        status = BoilerStatus('Name', 'desc', 'title', 'S.04', 'hint', datetime.datetime.now(), '', '')
        self.assertFalse(status.is_error)

    def test_status_no_code(self):
        status = BoilerStatus('Name', 'desc', 'title', None, 'hint', datetime.datetime.now(), '', '')
        self.assertFalse(status.is_error)

    def test_status_online(self):
        status = BoilerStatus('Name', 'desc', 'title', None, 'hint', datetime.datetime.now(), 'ONLINE', '')
        self.assertTrue(status.is_online)

    def test_status_offline(self):
        status = BoilerStatus('Name', 'desc', 'title', None, 'hint', datetime.datetime.now(), 'XXX', '')
        self.assertFalse(status.is_online)

    def test_status_up_to_date(self):
        status = BoilerStatus('Name', 'desc', 'title', None, 'hint', datetime.datetime.now(), '', 'UPDATE_NOT_PENDING')
        self.assertTrue(status.is_up_to_date)

    def test_status_not_up_to_date(self):
        status = BoilerStatus('Name', 'desc', 'title', None, 'hint', datetime.datetime.now(), '', 'UPDATE')
        self.assertFalse(status.is_up_to_date)
