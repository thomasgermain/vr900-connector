import json
import unittest
from datetime import date, timedelta

import responses

from tests.testutil import TestUtil
from vr900connector.api import Urls, Payloads
from vr900connector.model import HotWater, HeatingMode, QuickMode, QuickVeto, Room, Zone, Circulation, Constants
from vr900connector.systemmanager import SystemManager


class SystemManagerTest(unittest.TestCase):

    def setUp(self):
        self.manager = SystemManager('user', 'pass', 'vr900-connector', TestUtil.temp_path())

    @responses.activate
    def test_system(self):
        serial = TestUtil.mock_full_auth_success()

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            rooms_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            system_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hvacstate'), 'r') as file:
            hvacstate_data = json.loads(file.read())

        self._mock_urls(hvacstate_data, livereport_data, rooms_data, serial, system_data)

        system = self.manager.get_system()

        self.assertIsNotNone(system)

        self.assertEqual(2, len(system.zones))
        self.assertEqual(4, len(system.rooms))

    @responses.activate
    def test_get_hot_water(self):
        serial = TestUtil.mock_full_auth_success()

        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            livereport_data = json.loads(file.read())

        with open(TestUtil.path('files/responses/hotwater'), 'r') as file:
            raw_hotwater = json.loads(file.read())

        responses.add(responses.GET, Urls.hot_water('Control_DHW').format(serial_number=serial), json=raw_hotwater,
                      status=200)

        responses.add(responses.GET, Urls.live_report().format(serial_number=serial), json=livereport_data,
                      status=200)

        param = HotWater('Control_DHW', None, None, None, None, None)
        hot_water = self.manager.get_hot_water(param)

        self.assertIsNotNone(hot_water)

        self.assertEqual(Urls.live_report().format(serial_number=serial), responses.calls[-1].request.url)
        self.assertEqual(Urls.hot_water('Control_DHW').format(serial_number=serial), responses.calls[-2].request.url)

    def test_set_hot_water_setpoint_temperature_no_value(self):
        self.assertFalse(self.manager.set_hot_water_setpoint_temperature(None, 18))
        self.assertFalse(self.manager.set_hot_water_setpoint_temperature(HotWater('id', 'name', None, 50, 55,
                                                                                  HeatingMode.AUTO), None))

    @responses.activate
    def test_set_hot_water_setpoint_temperature(self):
        serial = TestUtil.mock_full_auth_success()

        hotwater = HotWater('id', 'name', None, 50, 55, HeatingMode.AUTO)
        url = Urls.hot_water_temperature_setpoint(hotwater.id)
        payload = Payloads.hotwater_temperature_setpoint(60)

        responses.add(responses.PUT, url.format(serial_number=serial), status=200)

        self.assertTrue(self.manager.set_hot_water_setpoint_temperature(hotwater, 60))
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_quick_mode_no_current_quick_mode(self):
        serial = TestUtil.mock_full_auth_success()

        url = Urls.system_quickmode()
        payload = Payloads.quickmode(QuickMode.QM_VENTILATION_BOOST.name)

        responses.add(responses.PUT, url.format(serial_number=serial), status=200)

        self.assertTrue(self.manager.set_quick_mode(None, QuickMode.QM_VENTILATION_BOOST))
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

    def test_set_quick_mode_existing_quick_mode(self):
        TestUtil.mock_full_auth_success()
        self.assertFalse(self.manager.set_quick_mode(QuickMode.QM_SYSTEM_OFF, QuickMode.QM_VENTILATION_BOOST))

    def test_set_quick_mode_no_new_quick_mode(self):
        TestUtil.mock_full_auth_success()
        self.assertFalse(self.manager.set_quick_mode(None, None))

    @responses.activate
    def test_logout(self):
        TestUtil.mock_logout()
        self.manager.logout()

        self.assertEqual(Urls.logout(), responses.calls[-1].request.url)

    @responses.activate
    def test_set_quick_veto_room(self):
        serial_number = TestUtil.mock_full_auth_success()
        url = Urls.room_quick_veto(1).format(serial_number=serial_number)

        quick_veto = QuickVeto(100, 25)
        room = Room(1, 'Room', None, 15, 20, HeatingMode.AUTO, None, False, False, None)
        responses.add(responses.PUT, url, status=200)

        self.assertTrue(self.manager.set_room_quick_veto(room, quick_veto))
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_quick_veto_room_no_quick_veto(self):
        TestUtil.mock_full_auth_success()

        room = Room(1, 'Room', None, 15, 20, HeatingMode.AUTO, None, False, False, None)
        self.assertFalse(self.manager.set_room_quick_veto(room, None))

    def test_set_quick_veto_room_no_room(self):
        TestUtil.mock_full_auth_success()

        quick_veto = QuickVeto(100, 25)
        self.assertFalse(self.manager.set_room_quick_veto(None, quick_veto))

    def test_set_hot_water_operation_mode_no_new_mode(self):
        hotwater = HotWater('hotwater', 'hotwater', None, 25, 30, HeatingMode.AUTO)
        self.assertFalse(self.manager.set_hot_water_operation_mode(hotwater, None))

    def test_set_hot_water_operation_mode_no_hotwater(self):
        self.assertFalse(self.manager.set_hot_water_operation_mode(None, HeatingMode.ON))

    def test_set_hot_water_operation_mode_wrong_mode(self):
        hotwater = HotWater('hotwater', 'hotwater', None, 25, 30, HeatingMode.AUTO)
        self.assertFalse(self.manager.set_hot_water_operation_mode(hotwater, HeatingMode.NIGHT))

    @responses.activate
    def test_set_hot_water_operation_mode_heating_mode(self):
        serial_number = TestUtil.mock_full_auth_success()

        url = Urls.hot_water_operation_mode('hotwater').format(serial_number=serial_number)
        hotwater = HotWater('hotwater', 'hotwater', None, 25, 30, HeatingMode.AUTO)

        responses.add(responses.PUT, url, status=200)
        self.assertTrue(self.manager.set_hot_water_operation_mode(hotwater, HeatingMode.ON))
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_set_quick_veto_zone(self):
        serial_number = TestUtil.mock_full_auth_success()
        url = Urls.zone_quick_veto("Zone1").format(serial_number=serial_number)

        quick_veto = QuickVeto(100, 25)
        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)
        responses.add(responses.PUT, url, status=200)

        self.assertTrue(self.manager.set_zone_quick_veto(zone, quick_veto))
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_quick_veto_zone_no_quick_veto(self):
        TestUtil.mock_full_auth_success()

        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)
        self.assertFalse(self.manager.set_zone_quick_veto(zone, None))

    def test_set_quick_veto_zone_no_zone(self):
        TestUtil.mock_full_auth_success()

        quick_veto = QuickVeto(100, 25)
        self.assertFalse(self.manager.set_zone_quick_veto(None, quick_veto))

    @responses.activate
    def test_set_room_operation_mode_heating_mode(self):
        serial_number = TestUtil.mock_full_auth_success()

        url = Urls.room_operation_mode(1).format(serial_number=serial_number)
        room = Room(1, 'Room', None, 15, 20, HeatingMode.AUTO, None, False, False, None)

        responses.add(responses.PUT, url, status=200)
        self.assertTrue(self.manager.set_room_operation_mode(room, HeatingMode.AUTO))
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_room_operation_mode_no_new_mode(self):
        room = Room(1, 'Room', None, 15, 20, HeatingMode.AUTO, None, False, False, None)
        self.assertFalse(self.manager.set_room_operation_mode(room, None))

    def test_set_room_operation_mode_no_room(self):
        self.assertFalse(self.manager.set_room_operation_mode(None, HeatingMode.MANUAL))

    def test_set_room_operation_mode_wrong_mode(self):
        room = Room(1, 'Room', None, 15, 20, HeatingMode.AUTO, None, False, False, None)
        self.assertFalse(self.manager.set_room_operation_mode(room, HeatingMode.NIGHT))

    @responses.activate
    def test_set_zone_operation_mode_heating_mode(self):
        serial_number = TestUtil.mock_full_auth_success()

        url = Urls.zone_heating_mode('Zone1').format(serial_number=serial_number)
        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)

        responses.add(responses.PUT, url, status=200)
        self.assertTrue(self.manager.set_zone_operation_mode(zone, HeatingMode.AUTO))
        self.assertEqual(url, responses.calls[-1].request.url)

    def test_set_zone_operation_mode_no_new_mode(self):
        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)
        self.assertFalse(self.manager.set_zone_operation_mode(zone, None))

    def test_set_zone_operation_mode_no_zone(self):
        self.assertFalse(self.manager.set_zone_operation_mode(None, HeatingMode.MANUAL))

    def test_set_zone_operation_mode_wrong_mode(self):
        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)
        self.assertFalse(self.manager.set_zone_operation_mode(zone, HeatingMode.ON))

    @responses.activate
    def test_get_room(self):
        serial = TestUtil.mock_full_auth_success()

        r1 = Room(1, "name1", None, None, None, None, None, False, False, [])

        with open(TestUtil.path('files/responses/room'), 'r') as file:
            raw_rooms = json.loads(file.read())

        responses.add(responses.GET, Urls.room(r1.id).format(serial_number=serial), json=raw_rooms,
                      status=200)

        new_room = self.manager.get_room(r1)
        self.assertIsNotNone(new_room)

    @responses.activate
    def test_get_zone(self):
        serial = TestUtil.mock_full_auth_success()

        zone = Zone('Control_ZO2', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)

        with open(TestUtil.path('files/responses/zone'), 'r') as file:
            raw_zone = json.loads(file.read())

        responses.add(responses.GET, Urls.zone(zone.id).format(serial_number=serial), json=raw_zone,
                      status=200)

        new_zone = self.manager.get_zone(zone)
        self.assertIsNotNone(new_zone)

    @responses.activate
    def test_get_circulation(self):
        serial_number = TestUtil.mock_full_auth_success()

        with open(TestUtil.path('files/responses/circulation'), 'r') as file:
            raw_circulation = json.loads(file.read())

        responses.add(responses.GET, Urls.circulation('id_dhw').format(serial_number=serial_number),
                      json=raw_circulation, status=200)

        new_circulation = self.manager.get_circulation(Circulation('id_dhw', None, None, None))
        self.assertIsNotNone(new_circulation)

    def test_set_room_setpoint_temperature_no_value(self):
        self.assertFalse(self.manager.set_room_setpoint_temperature(None, 18))
        self.assertFalse(self.manager.set_room_setpoint_temperature(Room('id', 'name', None, 15, 15, None, None, False,
                                                                         False, []), None))

    @responses.activate
    def test_set_room_setpoint_temperature(self):
        serial = TestUtil.mock_full_auth_success()

        room = Room(1, 'Room', None, 15, 20, HeatingMode.AUTO, None, False, False, None)
        url = Urls.room_set_temperature_setpoint(room.id)
        payload = Payloads.room_temperature_setpoint(22)

        responses.add(responses.PUT, url.format(serial_number=serial), status=200)

        self.assertTrue(self.manager.set_room_setpoint_temperature(room, 22))
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

    def test_set_zone_setpoint_temperature_no_value(self):
        self.assertFalse(self.manager.set_zone_setpoint_temperature(None, 18))
        self.assertFalse(
            self.manager.set_zone_setpoint_temperature(Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20,
                                                            'Heating', False), None))

    @responses.activate
    def test_set_zone_setpoint_temperature(self):
        serial = TestUtil.mock_full_auth_success()

        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)
        url = Urls.zone_heating_setpoint_temperature(zone.id)
        payload = Payloads.zone_temperature_setpoint(25)

        responses.add(responses.PUT, url.format(serial_number=serial), status=200)

        self.assertTrue(self.manager.set_zone_setpoint_temperature(zone, 25))
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

    def test_set_zone_setback_temperature_no_value(self):
        self.assertFalse(self.manager.set_zone_setback_temperature(None, 18))
        self.assertFalse(
            self.manager.set_zone_setback_temperature(Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20,
                                                           'Heating', False), None))

    @responses.activate
    def test_set_zone_setback_temperature(self):
        serial = TestUtil.mock_full_auth_success()

        zone = Zone('Zone1', 'Zone1', None, 20, 22, HeatingMode.AUTO, None, 20, 'Heating', False)
        url = Urls.zone_heating_setback_temperature(zone.id)
        payload = Payloads.zone_temperature_setback(18)

        responses.add(responses.PUT, url.format(serial_number=serial), status=200)

        self.assertTrue(self.manager.set_zone_setback_temperature(zone, 18))
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_set_holiday_mode(self):
        serial = TestUtil.mock_full_auth_success()

        tomorrow = date.today() + timedelta(days=1)
        after_tomorrow = tomorrow + timedelta(days=1)

        url = Urls.system_holiday_mode()
        responses.add(responses.PUT, url.format(serial_number=serial), status=200)
        payload = Payloads.holiday_mode(True, tomorrow, after_tomorrow, 15)

        self.assertTrue(self.manager.set_holiday_mode(tomorrow, after_tomorrow, 15))
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

        return True

    @responses.activate
    def test_remove_holiday_mode(self):
        serial = TestUtil.mock_full_auth_success()

        yesterday = date.today() - timedelta(days=1)
        before_yesterday = yesterday - timedelta(days=1)

        url = Urls.system_holiday_mode()
        responses.add(responses.PUT, url.format(serial_number=serial), status=200)
        payload = Payloads.holiday_mode(False, before_yesterday, yesterday, Constants.FROST_PROTECTION_TEMP)

        self.assertTrue(self.manager.remove_holiday_mode())
        self.assertEqual(json.dumps(payload), responses.calls[-1].request.body.decode('utf-8'))

    @responses.activate
    def test_remove_zone_quick_veto(self):
        serial = TestUtil.mock_full_auth_success()

        zone = Zone('id', None, None, None, None, None, None, None, None, None)

        url = Urls.zone_quick_veto(zone.id).format(serial_number=serial)
        responses.add(responses.DELETE, url, status=200)

        self.assertTrue(self.manager.remove_zone_quick_veto(zone))
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_remove_room_quick_veto(self):
        serial = TestUtil.mock_full_auth_success()

        room = Room('id', None, None, None, None, None, None, None, None, None)

        url = Urls.room_quick_veto(room.id).format(serial_number=serial)
        responses.add(responses.DELETE, url, status=200)

        self.assertTrue(self.manager.remove_room_quick_veto(room))
        self.assertEqual(url, responses.calls[-1].request.url)

    @responses.activate
    def test_request_hvac_update(self):
        serial = TestUtil.mock_full_auth_success()

        url = Urls.hvac_update().format(serial_number=serial)
        responses.add(responses.PUT, url, status=200)

        self.assertTrue(self.manager.request_hvac_update())
        self.assertEqual(url, responses.calls[-1].request.url)

    def _mock_urls(self, hvacstate_data, livereport_data, rooms_data, serial, system_data):
        responses.add(responses.GET, Urls.live_report().format(serial_number=serial), json=livereport_data,
                      status=200)
        responses.add(responses.GET, Urls.rooms().format(serial_number=serial), json=rooms_data, status=200)
        responses.add(responses.GET, Urls.system().format(serial_number=serial), json=system_data, status=200)
        responses.add(responses.GET, Urls.hvac().format(serial_number=serial), json=hvacstate_data, status=200)


if __name__ == '__main__':
    unittest.main()
