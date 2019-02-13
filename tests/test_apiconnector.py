import json
import unittest
from string import Template

import responses

from vr900connector.api import constant, ApiError, ApiConnector
from tests.testutil import TestUtil


class ApiConnectorTest(unittest.TestCase):

    def setUp(self):
        self.connector = ApiConnector('user', 'pass', 'vr900-connector', 'https://mock.com', TestUtil.temp_path())

    def tearDown(self):
        if self.connector:
            self.connector.close_session(True)

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

        data = self.connector.get_facilities()
        self.assertEqual(data, facilities_data)
        self.assertEqual(len(responses.calls), 4)
        self.assertEqual(responses.calls[0].request.url, 'https://mock.com/account/authentication/v1/token/new')
        self.assertEqual(responses.calls[1].request.url, 'https://mock.com/account/authentication/v1/authenticate')
        self.assertEqual(responses.calls[2].request.url, 'https://mock.com/facilities')
        self.assertEqual(responses.calls[3].request.url, 'https://mock.com/facilities')

    @responses.activate
    def test_re_login(self):
        TestUtil.mock_auth()

        responses.add(responses.GET, 'https://mock.com/test', status=401)

        try:
            self.connector.get('test')
            self.fail('Error expected')
        except ApiError as e:
            self.assertEqual(e.response.status_code, 401)
            self.assertEqual(e.response.url, 'https://mock.com/test')
            self.assertEqual(responses.calls[3].request.url, 'https://mock.com/test')
            self.assertEqual(responses.calls[7].request.url, 'https://mock.com/test')

    @responses.activate
    def test_cookie_failed(self):
        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=401)

        try:
            self.connector.get_facilities()
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual(e.message, "Cannot get cookies")

    @responses.activate
    def test_login_wrong_authentication(self):
        with open(TestUtil.path('files/responses/wrong_token'), 'r') as file:
            token_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new', json=token_data,
                      status=401)

        try:
            self.connector.get_facilities()
            self.fail("Error expected")
        except ApiError as e:
            self.assertEqual(e.message, "Authentication failed")

    @responses.activate
    def test_get(self):
        TestUtil.mock_auth()

        responses.add(responses.GET, 'https://mock.com/1234567890123456789012345678/123', json={"message": "123"},
                      status=200)

        response = self.connector.get("/$serialNumber/123")
        self.assertIsNotNone(response)
        self.assertEqual('123', response['message'])

    @responses.activate
    def test_get_circulation(self):
        TestUtil.mock_auth()

        responses.add(responses.GET, 'https://mock.com/facilities/1234567890123456789012345678/systemcontrol/v1/dhw/'
                                     'Control_DHW/circulation', json={"mock": "123"}, status=200)

        response = self.connector.get_circulation('Control_DHW')
        self.assertIsNotNone(response)
        self.assertEqual('123', response['mock'])

    @responses.activate
    def test_get_hotwater(self):
        TestUtil.mock_auth()

        responses.add(responses.GET, 'https://mock.com/facilities/1234567890123456789012345678/systemcontrol/v1/dhw/'
                                     'Control_DHW/hotwater', json={"mock": "123"}, status=200)

        response = self.connector.get_hotwater('Control_DHW')
        self.assertIsNotNone(response)
        self.assertEqual('123', response['mock'])

    @responses.activate
    def test_set_hot_water_setpoint_temperature(self):
        TestUtil.mock_auth()

        url = 'https://mock.com' + Template(constant.DHW_HOTWATER_SET_POINT_TEMPERATURE_URL)\
            .substitute(dhwIdentifier='Control_DHW', serialNumber='1234567890123456789012345678')

        responses.add(responses.PUT, url, status=200)

        response = self.connector.set_hotwater_setpoint_temperature('Control_DHW', 185)
        self.assertIsNotNone(response)
        self.assertIsNotNone('ok', response['ok'])
        self.assertEqual('ok', response['ok'])
        self.assertEqual(responses.calls[3].request.url, url)
        self.assertEqual(responses.calls[3].request.body.decode(), '{"temperature_setpoint": 185}')
        self.assertEqual(responses.calls[3].response.status_code, 200)

    #set_hot_water_operation_mode
    #remove_quick_mode
    #set_quick_mode



if __name__ == '__main__':
    unittest.main()
