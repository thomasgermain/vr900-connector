import json
import unittest
from datetime import date

from .testutil import TestUtil
from vr900connector.modelmapper import Mapper
from vr900connector import constant


class ModelMapperTest(unittest.TestCase):

    def setUp(self):
        self.mapper = Mapper()

    def test_map_quick_mode(self):
        with open(TestUtil.path("files/responses/systemcontrol_hotwater_boost"), 'r') as file:
            system = json.loads(file.read())

        quick_mode = self.mapper.quick_mode(system)
        self.assertEqual(constant.HOT_WATER_MODE_BOOST, quick_mode.boostMode.name)
        self.assertEqual(0, quick_mode.remainingDuration)

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
        self.assertEqual(constant.THERMOSTAT_ROOM_MODE_AUTO, room0.operationMode)
        self.assertEqual(False, room0.isWindowOpen)
        self.assertEqual(17.5, room0.targetTemperature)
        self.assertEqual(17.9, room0.currentTemperature)
        self.assertIsNone(room0.quickVeto)
        self.assertEqual(False, room0.childLock)

    def test_room_quick_veto(self):
        with open(TestUtil.path('files/responses/rooms_quick_veto'), 'r') as file:
            raw_rooms = json.loads(file.read())

        rooms = self.mapper.rooms(raw_rooms)
        self.assertIsNotNone(rooms)
        self.assertEqual(4, len(rooms))

        room0 = rooms[0]

        self.assertEqual(0, room0.id)
        self.assertEqual("Room 1", room0.name)
        self.assertEqual(constant.THERMOSTAT_ROOM_MODE_AUTO, room0.operationMode)
        self.assertEqual(False, room0.isWindowOpen)
        self.assertEqual(20.0, room0.targetTemperature)
        self.assertEqual(17.9, room0.currentTemperature)
        self.assertIsNotNone(room0.quickVeto)
        self.assertEqual(20.0, room0.quickVeto.targetTemperature)
        self.assertEqual(180, room0.quickVeto.remainingTime)
        self.assertEqual(False, room0.childLock)

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
        self.assertEqual("VALVE", devices_room0[0].deviceType)
        self.assertEqual(True, devices_room0[0].isRadioOutOfReach)
        self.assertEqual(True, devices_room0[0].isRadioOutOfReach)

        self.assertEqual("Device 1", devices_room1[0].name)
        self.assertEqual("R20123456789012345678900", devices_room1[0].sgtin)
        self.assertEqual("VALVE", devices_room1[0].deviceType)
        self.assertEqual(False, devices_room1[0].isRadioOutOfReach)
        self.assertEqual(False, devices_room1[0].isRadioOutOfReach)

        self.assertEqual("Device 2", devices_room1[1].name)
        self.assertEqual("R20123456789012345678999", devices_room1[1].sgtin)
        self.assertEqual("VALVE", devices_room1[1].deviceType)
        self.assertEqual(False, devices_room1[1].isRadioOutOfReach)
        self.assertEqual(False, devices_room1[1].isRadioOutOfReach)

    def test_holiday_mode_none(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())

        holiday_mode = self.mapper.holiday_mode(raw_system)
        self.assertIsNotNone(holiday_mode)
        self.assertFalse(holiday_mode.active)
        self.assertIsNone(holiday_mode.startDate)
        self.assertIsNone(holiday_mode.endDate)
        self.assertIsNone(holiday_mode.targetTemperature)

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
        self.assertEqual(constant.CIRCULATION_MODE_AUTO, circulation.operationMode)
        self.assertEqual("Control_DHW", circulation.id)
        self.assertEqual(0, circulation.currentTemperature)
        self.assertEqual(0, circulation.targetTemperature)

    def test_hot_water(self):
        with open(TestUtil.path('files/responses/systemcontrol'), 'r') as file:
            raw_system = json.loads(file.read())
        with open(TestUtil.path('files/responses/livereport'), 'r') as file:
            raw_livereport = json.loads(file.read())

        hot_water = self.mapper.domestic_hot_water(raw_system, raw_livereport)
        self.assertEqual(44.5, hot_water.currentTemperature)
        self.assertEqual(51, hot_water.targetTemperature)
        self.assertEqual(constant.HOT_WATER_MODE_AUTO, hot_water.operationMode)
        self.assertEqual("Control_DHW", hot_water.id)


if __name__ == '__main__':
    unittest.main()
