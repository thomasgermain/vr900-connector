import json
import unittest

import responses

from .testutil import TestUtil
from vr900connector.api.apiconnector import ApiConnector
from vr900connector.api.apierror import ApiError


class ApiConnectorTest(unittest.TestCase):

    def mock_authentication(self):
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=200)
        responses.add(responses.GET, 'https://mock.com/facilities', json=facilities_data, status=200)

    @responses.activate
    def test_login(self):
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=200)
        responses.add(responses.GET, 'https://mock.com/facilities', json=facilities_data, status=200)

        connector = ApiConnector('user', 'pass', 'vr900-connector', 'https://mock.com', TestUtil.temp_path())

        data = connector.get_facilities()
        self.assertEqual(data, facilities_data)

    @responses.activate
    def test_cookie_failed(self):
        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=401)

        connector = ApiConnector('user', 'pass', 'vr900-connector', 'https://mock.com', TestUtil.temp_path())

        try:
            connector.get_facilities()
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual(e.message, "Cannot get cookies")

    @responses.activate
    def test_login_wrong_authentication(self):
        with open(TestUtil.path('files/responses/wrong_token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=401)

        connector = ApiConnector('user', 'pass', 'vr900-connector', 'https://mock.com', TestUtil.temp_path())

        try:
            connector.get_facilities()
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual(e.message, "Authentication failed")

    @responses.activate
    def test_get(self):
        self.mock_authentication()

        responses.add(responses.GET, 'https://mock.com/1234567890123456789012345678/123', json={"message": "123"},
                      status=200)

        connector = ApiConnector('user', 'pass', 'vr900-connector', 'https://mock.com', TestUtil.temp_path())

        response = connector.get("/{serialNumber}/123")
        self.assertIsNotNone(response)
        self.assertIsNotNone('123', response['message'])


if __name__ == '__main__':
    unittest.main()
