import json
import unittest
from unittest.mock import Mock

import responses

from tests.testutil import TestUtil
from vr900connector.api import Urls, ApiError, ApiConnector


class ApiConnectorTest(unittest.TestCase):

    def setUp(self):
        self.connector = ApiConnector('user', 'pass', 'vr900-connector', TestUtil.temp_path())

    @responses.activate
    def tearDown(self):
        if self.connector:
            TestUtil.mock_logout()
            self.connector.logout()

    @responses.activate
    def test_login(self):
        TestUtil.mock_full_auth_success()

        self.connector.get(Urls.facilities_list())
        self.assertEqual(4, len(responses.calls))
        self.assertEqual(Urls.new_token(), responses.calls[0].request.url)
        self.assertEqual(Urls.authenticate(), responses.calls[1].request.url)
        self.assertEqual(Urls.facilities_list(), responses.calls[2].request.url)
        self.assertEqual(Urls.facilities_list(), responses.calls[3].request.url)

    @responses.activate
    def test_re_login(self):
        serial_number = TestUtil.mock_full_auth_success()

        repeaters_url = Urls.repeaters().format(serial_number=serial_number)
        responses.add(responses.GET, repeaters_url, status=401)

        try:
            self.connector.get(Urls.repeaters())
            self.fail('Error expected')
        except ApiError as e:
            self.assertEqual(8, len(responses.calls))
            self.assertEqual(401, e.response.status_code)
            self.assertEqual(repeaters_url, e.response.url)
            self.assertEqual(repeaters_url, responses.calls[3].request.url)
            self.assertEqual(repeaters_url, responses.calls[7].request.url)

    @responses.activate
    def test_cookie_failed(self):
        TestUtil.mock_token_success()

        responses.add(responses.POST, Urls.authenticate(), status=401)

        try:
            self.connector.get(Urls.facilities_list())
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Cannot get cookies", e.message)

    @responses.activate
    def test_cookie_failed_exception(self):
        TestUtil.mock_token_success()

        try:
            self.connector.get(Urls.facilities_list())
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Error while getting cookies", e.message)
            self.assertIsNone(e.response)

    @responses.activate
    def test_login_wrong_authentication(self):
        with open(TestUtil.path('files/responses/wrong_token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, Urls.new_token(), json=token_data, status=401)

        try:
            self.connector.get(Urls.facilities_list())
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Authentication failed", e.message)

    @responses.activate
    def test_put(self):
        serial = TestUtil.mock_full_auth_success()

        responses.add(responses.PUT, Urls.rooms().format(serial_number=serial), json='', status=200)
        self.connector.put(Urls.rooms())

        self.assertEqual(4, len(responses.calls))
        self.assertEqual('PUT', responses.calls[3].request.method)

    @responses.activate
    def test_post(self):
        serial = TestUtil.mock_full_auth_success()

        responses.add(responses.POST, Urls.rooms().format(serial_number=serial), json='', status=200)
        self.connector.post(Urls.rooms())

        self.assertEqual(4, len(responses.calls))
        self.assertEqual('POST', responses.calls[3].request.method)

    @responses.activate
    def test_delete(self):
        serial = TestUtil.mock_full_auth_success()

        responses.add(responses.DELETE, Urls.rooms().format(serial_number=serial), json='', status=200)
        self.connector.delete(Urls.rooms())

        self.assertEqual(4, len(responses.calls))
        self.assertEqual('DELETE', responses.calls[3].request.method)

    @responses.activate
    def test_cannot_get_serial(self):
        TestUtil.mock_authentication_success()
        TestUtil.mock_token_success()

        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Cannot get serial number", e.message)
            self.assertIsNone(e.response)

    @responses.activate
    def test_cannot_get_serial_bad_request(self):
        TestUtil.mock_authentication_success()
        TestUtil.mock_token_success()

        responses.add(responses.GET, Urls.facilities_list(), json='', status=400)

        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Cannot get serial number", e.message)
            self.assertIsNotNone(e.response)
            self.assertEqual(400, e.response.status_code)

    @responses.activate
    def test_logout_failed(self):
        TestUtil.mock_full_auth_success()

        try:
            self.connector.logout()
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Error during logout", e.message)
            self.assertIsNone(self.connector._serial_number)
            self.assertEqual(0, len(self.connector._session.cookies))

    @responses.activate
    def test_call_empty_response_success(self):
        serial = TestUtil.mock_full_auth_success()

        responses.add(responses.GET, Urls.rooms().format(serial_number=serial), status=200)

        result = self.connector.get(Urls.rooms())
        self.assertEqual({"ok": "ok"}, result)

    @responses.activate
    def test_call_error(self):
        serial = TestUtil.mock_full_auth_success()

        try:
            self.connector.get(Urls.rooms())
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual("Cannot GET url: " + Urls.rooms().format(serial_number=serial), e.message)

    @responses.activate
    def test_request_token_error(self):
        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as e:
            self.assertIsNone(e.response)
            self.assertEqual('Error during authentication', e.message)

    @responses.activate
    def test_login_error(self):
        try:
            self.connector.get('')
            self.fail("Error expected")
        except ApiError as e:
            self.assertIsNone(e.response)
            self.assertEqual('Error during authentication', e.message)

    @responses.activate
    def test_login_catch_exception(self):
        TestUtil.mock_full_auth_success()

        self.connector._create_or_load_session = Mock(side_effect=Exception('Test exception'))
        self.connector._session.cookies = None

        try:
            self.connector.get('')
        except ApiError as e:
            self.assertIsNone(e.response)
            self.assertEqual('Error during login', e.message)

    @responses.activate
    def test_login_once(self):
        TestUtil.mock_full_auth_success()

        self.connector.get(Urls.facilities_list())
        self.connector.get(Urls.facilities_list())
        self.assertEqual(5, len(responses.calls))
        self.assertEqual(Urls.new_token(), responses.calls[0].request.url)
        self.assertEqual(Urls.authenticate(), responses.calls[1].request.url)
        self.assertEqual(Urls.facilities_list(), responses.calls[2].request.url)
        self.assertEqual(Urls.facilities_list(), responses.calls[3].request.url)
        self.assertEqual(Urls.facilities_list(), responses.calls[4].request.url)

    @responses.activate
    def test_login_loaded_session(self):

        TestUtil.mock_full_auth_success()
        self.connector = ApiConnector('user', 'pass', 'vr900-connector', TestUtil.path('./files/session'))

        # Do nothing on clear session, otherwise it will delete files in tests/files/session
        self.connector._clear_session = Mock()

        self.connector.get(Urls.facilities_list())

        self.assertEqual(1, len(responses.calls))
        self.assertEqual(Urls.facilities_list(), responses.calls[0].request.url)

    @responses.activate
    def test_login_loaded_session_no_serial(self):

        TestUtil.mock_full_auth_success()
        self.connector = ApiConnector('user', 'pass', 'vr900-connector', TestUtil.path('./files/session'))

        # Do nothing on clear session, otherwise it will delete files in tests/files/session
        self.connector._clear_session = Mock()
        self.connector._serial_number = None

        self.connector.get(Urls.facilities_list())

        self.assertEqual(2, len(responses.calls))
        self.assertEqual(Urls.facilities_list(), responses.calls[0].request.url)
        self.assertEqual(Urls.facilities_list(), responses.calls[1].request.url)


if __name__ == '__main__':
    unittest.main()
