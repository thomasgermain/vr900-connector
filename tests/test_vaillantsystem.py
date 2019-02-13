import json
import unittest

import responses

from vr900connector.util import UrlFormatter
from vr900connector.model.constant import THERMOSTAT_QUICK_VETO, QM_HOTWATER_BOOST, FROST_PROTECTION_TEMP, QM_SYSTEM_OFF
from vr900connector.vaillantsystemmanager import VaillantSystemManager
from tests.testutil import TestUtil
from vr900connector.api import constant


class VaillantSystemTest(unittest.TestCase):

    @responses.activate
    def test_system(self):
        serial = TestUtil.mock_auth()

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            system_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        responses.add(responses.GET, 'https://mock.com' + UrlFormatter.format(constant.LIVE_REPORT_URL, serial),
                      json=livereport_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + UrlFormatter.format(constant.ROOMS_URL, serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + UrlFormatter.format(constant.SYSTEM_CONTROL_URL, serial),
                      json=system_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + UrlFormatter.format(constant.HVAC_STATE_URL, serial),
                      json=hvacstate_data, status=200)

        manager = VaillantSystemManager("user", "pass", "test", "https://mock.com", TestUtil.temp_path())
        system = manager.get_system()

        self.assertIsNotNone(system)

        self.assertEqual(2, len(system.get_zones()))
        self.assertEqual(4, len(system.get_rooms()))

    @responses.activate
    def test_active_mode_hot_water_boost(self):
        TestUtil.mock_auth()

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

        responses.add(responses.GET, 'https://mock.com' + constant.FACILITIES_URL, json=facilities_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.LIVE_REPORT_URL.replace("$serialNumber", serial),
                      json=livereport_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.ROOMS_URL.replace("$serialNumber", serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.SYSTEM_CONTROL_URL.replace("$serialNumber", serial),
                      json=system_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.HVAC_STATE_URL.replace("$serialNumber", serial),
                      json=hvacstate_data, status=200)

        manager = VaillantSystemManager("user", "pass", "test", "https://mock.com", TestUtil.temp_path())
        system = manager.get_system()

        self.assertIsNotNone(system)

        active_mode = system.get_active_mode_hot_water()
        self.assertEqual(QM_HOTWATER_BOOST, active_mode.name)
        self.assertEqual(51, active_mode.targetTemperature)
        self.assertIsNone(active_mode.sub_mode)

    @responses.activate
    def test_active_mode_system_off(self):
        TestUtil.mock_auth()

        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())
            serial = facilities_data["body"]["facilitiesList"][0]["serialNumber"]

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/systemcontrol_off'), 'r') as file:
            system_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        responses.add(responses.GET, 'https://mock.com' + constant.FACILITIES_URL, json=facilities_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.LIVE_REPORT_URL.replace("$serialNumber", serial),
                      json=livereport_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.ROOMS_URL.replace("$serialNumber", serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.SYSTEM_CONTROL_URL.replace("$serialNumber", serial),
                      json=system_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.HVAC_STATE_URL.replace("$serialNumber", serial),
                      json=hvacstate_data, status=200)

        manager = VaillantSystemManager("user", "pass", "test", "https://mock.com", TestUtil.temp_path())
        system = manager.get_system()

        self.assertIsNotNone(system)

        active_mode = system.get_active_mode_hot_water()
        self.assertEqual(QM_SYSTEM_OFF, active_mode.name)
        self.assertEqual(FROST_PROTECTION_TEMP, active_mode.targetTemperature)
        self.assertIsNone(active_mode.sub_mode)

        active_mode = system.get_active_mode_circulation()
        self.assertEqual(QM_SYSTEM_OFF, active_mode.name)
        self.assertEqual(0, active_mode.targetTemperature)
        self.assertIsNone(active_mode.sub_mode)

        for room in system.get_rooms():
            active_mode = system.get_active_mode_room(room)
            self.assertEqual(QM_SYSTEM_OFF, active_mode.name)
            self.assertEqual(FROST_PROTECTION_TEMP, active_mode.targetTemperature)
            self.assertIsNone(active_mode.sub_mode)

        for zone in system.get_zones():
            if not zone .rbr:
                active_mode = system.get_active_mode_zone(zone)
                self.assertEqual(QM_SYSTEM_OFF, active_mode.name)
                self.assertEqual(FROST_PROTECTION_TEMP, active_mode.targetTemperature)
                self.assertIsNone(active_mode.sub_mode)

    @responses.activate
    def test_active_mode_zone_quick_veto(self):
        TestUtil.mock_auth()

        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())
            serial = facilities_data["body"]["facilitiesList"][0]["serialNumber"]

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/systemcontrol_quick_veto'), 'r') as file:
            system_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        responses.add(responses.GET, 'https://mock.com' + constant.FACILITIES_URL, json=facilities_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.LIVE_REPORT_URL.replace("$serialNumber", serial),
                      json=livereport_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.ROOMS_URL.replace("$serialNumber", serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.SYSTEM_CONTROL_URL.replace("$serialNumber", serial),
                      json=system_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.HVAC_STATE_URL.replace("$serialNumber", serial),
                      json=hvacstate_data, status=200)

        manager = VaillantSystemManager("user", "pass", "test", "https://mock.com", TestUtil.temp_path())
        system = manager.get_system()

        self.assertIsNotNone(system)

        zone = system.get_zone("Control_ZO2")
        active_mode = system.get_active_mode_zone(zone)
        self.assertEqual(THERMOSTAT_QUICK_VETO, active_mode.name)
        self.assertEqual(18.5, active_mode.targetTemperature)
        self.assertIsNone(active_mode.sub_mode)

    @responses.activate
    def test_active_mode_room_quick_veto(self):
        TestUtil.mock_auth()

        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities_data = json.loads(file.read())
            serial = facilities_data["body"]["facilitiesList"][0]["serialNumber"]

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/rooms_quick_veto'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            system_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        responses.add(responses.GET, 'https://mock.com' + constant.FACILITIES_URL, json=facilities_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.LIVE_REPORT_URL.replace("$serialNumber", serial),
                      json=livereport_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.ROOMS_URL.replace("$serialNumber", serial),
                      json=rooms_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.SYSTEM_CONTROL_URL.replace("$serialNumber", serial),
                      json=system_data, status=200)
        responses.add(responses.GET, 'https://mock.com' + constant.HVAC_STATE_URL.replace("$serialNumber", serial),
                      json=hvacstate_data, status=200)

        manager = VaillantSystemManager("user", "pass", "test", "https://mock.com", TestUtil.temp_path())
        system = manager.get_system()

        self.assertIsNotNone(system)

        room = system.get_room(0)
        active_mode = system.get_active_mode_room(room)
        self.assertEqual(THERMOSTAT_QUICK_VETO, active_mode.name)
        self.assertEqual(20.0, active_mode.targetTemperature)
        self.assertIsNone(active_mode.sub_mode)
