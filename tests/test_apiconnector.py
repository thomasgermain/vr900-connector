import json
import unittest

import responses

from tests.testutil import TestUtil
from vr900connector.api import urls, ApiError, ApiConnector


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
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, urls.new_token(), json=token_data, status=200)
        responses.add(responses.POST, urls.authenticate(), status=200)
        responses.add(responses.GET, urls.facilities_list(), json=facilities_data, status=200)

        data = self.connector.get(urls.facilities_list())
        self.assertEqual(data, facilities_data)
        self.assertEqual(len(responses.calls), 4)
        self.assertEqual(responses.calls[0].request.url, urls.new_token())
        self.assertEqual(responses.calls[1].request.url, urls.authenticate())
        self.assertEqual(responses.calls[2].request.url, urls.facilities_list())
        self.assertEqual(responses.calls[3].request.url, urls.facilities_list())

    @responses.activate
    def test_re_login(self):
        serial_number = TestUtil.mock_auth_success()

        repeaters_url = urls.repeaters().format(serial_number=serial_number)
        responses.add(responses.GET, repeaters_url, status=401)

        try:
            self.connector.get(urls.repeaters())
            self.fail('Error expected')
        except ApiError as e:
            self.assertEqual(len(responses.calls), 8)
            self.assertEqual(e.response.status_code, 401)
            self.assertEqual(e.response.url, repeaters_url)
            self.assertEqual(responses.calls[3].request.url, repeaters_url)
            self.assertEqual(responses.calls[7].request.url, repeaters_url)

    @responses.activate
    def test_cookie_failed(self):
        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, urls.new_token(), json=token_data, status=200)
        responses.add(responses.POST, urls.authenticate(), status=401)

        try:
            self.connector.get(urls.facilities_list())
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual(e.message, "Cannot get cookies")

    @responses.activate
    def test_login_wrong_authentication(self):
        with open(TestUtil.path('files/responses/wrong_token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, urls.new_token(), json=token_data, status=401)

        try:
            self.connector.get(urls.facilities_list())
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual(e.message, "Authentication failed")

    # @responses.activate
    # def test_login_once(self):
    #     TestUtil.mock_auth_success()
    #
    #     self.connector.get(urls.facilities_list())
    #     self.connector.get(urls.facilities_list())
    #     self.assertEqual(len(responses.calls), 5)


if __name__ == '__main__':
    unittest.main()
