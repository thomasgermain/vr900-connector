import tempfile
import unittest
import uuid

import responses
from vr900connector.vr900connectorerror import Vr900ConnectorError
from vr900connector.vr900connector import Vr900Connector


class TestVr900Connector(unittest.TestCase):

    @responses.activate
    def simpleTest(self):
        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new',
                      json={
                          "body": {
                              "authToken": "a30ff8b5e2aa4519af455ad472409120"
                          },
                          "meta": {}
                      }, status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=200)

        facilities_data = {
            "body": {
                "facilitiesList": [
                    {
                        "serialNumber": "123",
                        "name": "Name",
                        "responsibleCountryCode": "BE",
                        "supportedBrand": "GREEN_BRAND_COMPATIBLE",
                        "capabilities": [
                            "ROOM_BY_ROOM",
                            "SYSTEMCONTROL_MULTIMATIC"
                        ],
                        "networkInformation": {
                            "macAddressEthernet": "12:34:56:78:91:23",
                            "macAddressWifiAccessPoint": "45:56:89:01:23:45",
                            "macAddressWifiClient": "78:90:12:34:56:78"
                        },
                        "firmwareVersion": "1.2.3"
                    }
                ]
            }
        }

        responses.add(responses.GET, 'https://mock.com/facilities', json=facilities_data, status=200)

        connector = Vr900Connector('user', 'pass', 'vr900-connector', 'https://mock.com',
                                   tempfile.gettempdir() + "/" + str(uuid.uuid4()))

        data = connector.facilities()
        self.assertEqual(data, facilities_data)

    @responses.activate
    def testLoginFail(self):
        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/token/new',
                      json={
                          "body": {
                              "authToken": "a30ff8b5e2aa4519af455ad472409120"
                          },
                          "meta": {}
                      }, status=200)

        responses.add(responses.POST, 'https://mock.com/account/authentication/v1/authenticate', status=401)

        connector = Vr900Connector('user', 'pass', 'vr900-connector', 'https://mock.com',
                                   tempfile.gettempdir() + "/" + str(uuid.uuid4()))

        try:
            connector.facilities()
            self.fail("Error expected")
        except Vr900ConnectorError as e:
            self.assertEqual(e.message, "Cannot generate token")


if __name__ == '__main__':
    unittest.main()
