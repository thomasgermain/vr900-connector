import json
import unittest

import responses

from vr900connector.vaillantsystemmanager import VaillantSystemManager
from .testutil import TestUtil
from vr900connector import constant


class VaillantSystemTest(unittest.TestCase):

    @responses.activate
    def test_active_mode(self):
        with open(TestUtil.path('files/responses/token'), 'r') as file:
            token_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())
            serial = facilities_data["body"]["facilitiesList"][0]["serialNumber"]

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/systemcontrol_hotwater_boost'), 'r') as file:
            system_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        responses.add(responses.POST, 'https://mock.com' + constant.REQUEST_NEW_TOKEN_URL, json=token_data,
                      status=200)
        responses.add(responses.POST, 'https://mock.com' + constant.AUTHENTICATE_URL, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.TEST_LOGIN_URL, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.FACILITIES_URL, json=facilities_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.LIVE_REPORT_URL.replace("{serialNumber}", serial),
                      json=livereport_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.ROOMS_URl.replace("{serialNumber}", serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.SYSTEM_CONTROL_URL.replace("{serialNumber}", serial),
                      json=system_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.HVAC_STATE_URL.replace("{serialNumber}", serial),
                      json=hvacstate_data, status=200)

        manager = VaillantSystemManager("user", "pass", "test", "https://mock.com", TestUtil.temp_path())
        system = manager.get_system()

        self.assertIsNotNone(system)

        active_mode = system.get_active_mode_hot_water()
        self.assertEqual(constant.HOT_WATER_MODE_BOOST, active_mode.name)
        self.assertEqual(51, active_mode.targetTemperature)
        self.assertIsNone(active_mode.sub_mode)

