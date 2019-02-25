import json
import unittest
from datetime import date

from tests.testutil import TestUtil
from vr900connector.model import Mapper, constants


class ModelMapperTest(unittest.TestCase):

    def setUp(self):
        self.mapper = Mapper()

    def test_map_quick_mode(self):
        with open(TestUtil.path("files/responses/systemcontrol_hotwater_boost"), 'r') as file:
            system = json.loads(file.read())

        quick_mode = self.mapper.quick_mode(system)
        self.assertEqual(constants.QM_HOTWATER_BOOST, quick_mode.name)

    def test_map_no_quick_mode(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            system = json.loads(file.read())

        quick_mode = self.mapper.quick_mode(system)
        self.assertIsNone(quick_mode)

    def test_map_outdoor_temp(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            system = json.loads(file.read())

        temp = self.mapper.outdoor_temp(system)
        self.assertEqual(6.3, temp)

    def test_map_no_outdoor_temp(self):
        with open(TestUtil.path('files/responses/systemcontrol_no_outside_temp'), 'r') as file:
            system = json.loads(file.read())

        temp = self.mapper.outdoor_temp(system)
        self.assertIsNone(temp)

    def test_installation_name(self):
        with open(TestUtil.path('files/responses/facilities'), 'r') as file:
            facilities = json.loads(file.read())

        name = self.mapper.installation_name(facilities)
        self.assertEqual("Home", name)

    def test_rooms_none(self):
        rooms = self.mapper.rooms(None)
        self.assertIsNotNone(rooms)
        self.assertEqual(0, len(rooms))

    def test_rooms_empty(self):
        rooms = self.mapper.rooms(dict())
        self.assertIsNotNone(rooms)
        self.assertEqual(0, len(rooms))

    def test_room_correct(self):
        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            raw_rooms = json.loads(file.read())

        rooms = self.mapper.rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        room0 = rooms[0]

        self.assertEqual(0, room0.id)
        self.assertEqual("Room 1", room0.name)
        self.assertEqual(constants.MODE_AUTO, room0.operation_mode)
        self.assertEqual(False, room0.window_open)
        self.assertEqual(17.5, room0.target_temperature)
        self.assertEqual(17.9, room0.current_temperature)
        self.assertIsNone(room0.quick_veto)
        self.assertEqual(False, room0.child_lock)

    def test_room_quick_veto(self):
        with open(TestUtil.path('files/responses/rooms_quick_veto'), 'r') as file:
            raw_rooms = json.loads(file.read())

        rooms = self.mapper.rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        room0 = rooms[0]

        self.assertEqual(0, room0.id)
        self.assertEqual("Room 1", room0.name)
        self.assertEqual(constants.MODE_AUTO, room0.operation_mode)
        self.assertEqual(False, room0.window_open)
        self.assertEqual(20.0, room0.target_temperature)
        self.assertEqual(17.9, room0.current_temperature)
        self.assertIsNotNone(room0.quick_veto)
        self.assertEqual(20.0, room0.quick_veto.target_temperature)
        self.assertEqual(False, room0.child_lock)

    def test_devices(self):
        with open(TestUtil.path('files/responses/rooms'), 'r') as file:
            raw_rooms = json.loads(file.read())

        rooms = self.mapper.rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        devices_room0 = rooms[0].devices
        devices_room1 = rooms[1].devices

        self.assertIsNotNone(devices_room0)
        self.assertEqual(1, len(devices_room0))
        self.assertIsNotNone(devices_room1)
        self.assertEqual(2, len(devices_room1))

        self.assertEqual("Device 1", devices_room0[0].name)
        self.assertEqual("R13456789012345678901234", devices_room0[0].sgtin)
        self.assertEqual("VALVE", devices_room0[0].device_type)
        self.assertEqual(True, devices_room0[0].radio_out_of_reach)
        self.assertEqual(True, devices_room0[0].radio_out_of_reach)

        self.assertEqual("Device 1", devices_room1[0].name)
        self.assertEqual("R20123456789012345678900", devices_room1[0].sgtin)
        self.assertEqual("VALVE", devices_room1[0].device_type)
        self.assertEqual(False, devices_room1[0].radio_out_of_reach)
        self.assertEqual(False, devices_room1[0].radio_out_of_reach)

        self.assertEqual("Device 2", devices_room1[1].name)
        self.assertEqual("R20123456789012345678999", devices_room1[1].sgtin)
        self.assertEqual("VALVE", devices_room1[1].device_type)
        self.assertEqual(False, devices_room1[1].radio_out_of_reach)
        self.assertEqual(False, devices_room1[1].radio_out_of_reach)

    def test_holiday_mode_none(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        holiday_mode = self.mapper.holiday_mode(raw_system)
        self.assertIsNotNone(holiday_mode)
        self.assertFalse(holiday_mode.active)
        self.assertIsNone(holiday_mode.start_date)
        self.assertIsNone(holiday_mode.end_date)
        self.assertIsNone(holiday_mode.target_temperature)

    def test_holiday_mode(self):
        with open(TestUtil.path('files/responses/systemcontrol_holiday'), 'r') as file:
            raw_system = json.loads(file.read())

        holiday_mode = self.mapper.holiday_mode(raw_system)
        self.assertIsNotNone(holiday_mode)
        self.assertTrue(holiday_mode.active)
        self.assertEqual(date(2019, 1, 2), holiday_mode.startDate)
        self.assertEqual(date(2019, 1, 3), holiday_mode.endDate)
        self.assertEqual(15, holiday_mode.targetTemperature)

    def test_circulation(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        circulation = self.mapper.circulation(raw_system)
        self.assertEqual(constants.MODE_AUTO, circulation.operation_mode)
        self.assertEqual("Control_DHW", circulation.id)
        self.assertIsNone(circulation.current_temperature)
        self.assertIsNone(circulation.target_temperature)

    def test_hot_water(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())
        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            raw_livereport = json.loads(file.read())

        hot_water = self.mapper.domestic_hot_water(raw_system, raw_livereport)
        self.assertEqual(44.5, hot_water.current_temperature)
        self.assertEqual(51, hot_water.target_temperature)
        self.assertEqual(constants.MODE_AUTO, hot_water.operation_mode)
        self.assertEqual("Control_DHW", hot_water.id)


if __name__ == '__main__':
    unittest.main()
