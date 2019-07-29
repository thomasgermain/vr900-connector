import json
import datetime
import unittest

from tests.testutil import TestUtil
from vr900connector.model import System, TimeProgram, TimeProgramDaySetting, TimeProgramDay, QuickMode, QuickVeto, \
    HolidayMode, Room, HotWater, Zone, Constants, Circulation, HeatingMode, Mapper


class SystemTest(unittest.TestCase):

    def test_get_active_mode_room(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, None)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        room = Room(1, 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, False, False, [])
        system = System(None, None, [], [room], None, None, 5, None, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertIsNone(active_mode.sub_mode)
        self.assertEqual(timeprogram_day_setting.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_room_quick_veto(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, None)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)
        quick_veto = QuickVeto(0, 22)

        room = Room(1, 'Test', timeprogram, 20, 20, HeatingMode.AUTO, quick_veto, False, False, [])
        system = System(None, None, [], [room], None, None, 5, None, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(HeatingMode.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(quick_veto.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_room_holiday_mode(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, None)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)
        holiday_mode = HolidayMode(True, datetime.date.today(), datetime.date.today(), 10)

        room = Room(1, 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, False, False, [])
        system = System(holiday_mode, None, [], [room], None, None, 5, None, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(QuickMode.QM_HOLIDAY, active_mode.current_mode)
        self.assertEqual(holiday_mode.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_room_system_off(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, None)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        room = Room(1, 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, False, False, [])
        system = System(None, None, [], [room], None, None, 5, QuickMode.QM_SYSTEM_OFF, [])

        active_mode = system.get_active_mode_room(room)

        self.assertEqual(QuickMode.QM_SYSTEM_OFF, active_mode.current_mode)
        self.assertEqual(Room.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_hot_water(self):
        with open(TestUtil.path('files/responses/hotwater_always_on'), 'r') as file:
            raw_hotwater = json.loads(file.read())

        hot_water = Mapper.domestic_hot_water_alone(raw_hotwater, 'id', None)

        system = System(None, None, [], [], hot_water, None, 5, None, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertEqual(HeatingMode.ON, active_mode.sub_mode)
        self.assertEqual(50, active_mode.target_temperature)

    def test_get_active_mode_hot_water_off(self):
        with open(TestUtil.path('files/responses/hotwater_always_off'), 'r') as file:
            raw_hotwater = json.loads(file.read())

        hot_water = Mapper.domestic_hot_water_alone(raw_hotwater, 'id', None)

        system = System(None, None, [], [], hot_water, None, 5, None, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertEqual(HeatingMode.OFF, active_mode.sub_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_hot_water_system_off(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 55, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55, HeatingMode.AUTO)
        system = System(None, None, [], [], hot_water, None, 5, QuickMode.QM_SYSTEM_OFF, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickMode.QM_SYSTEM_OFF, active_mode.current_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_hot_water_one_day_away(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 55, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55, HeatingMode.AUTO)
        system = System(None, None, [], [], hot_water, None, 5, QuickMode.QM_ONE_DAY_AWAY, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickMode.QM_ONE_DAY_AWAY, active_mode.current_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_hot_water_one_day_away(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 55, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55, HeatingMode.AUTO)
        system = System(None, None, [], [], hot_water, None, 5, QuickMode.QM_ONE_DAY_AWAY, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickMode.QM_ONE_DAY_AWAY, active_mode.current_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_hot_water_hot_water_boost(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 55, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55, HeatingMode.ON)
        system = System(None, None, [], [], hot_water, None, 5, QuickMode.QM_HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(active_mode.current_mode, QuickMode.QM_HOTWATER_BOOST)
        self.assertEqual(timeprogram_day_setting.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_hot_water_holiday_mode(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 55, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)
        holiday_mode = HolidayMode(True, datetime.date.today(), datetime.date.today(), 10)

        hot_water = HotWater('test', 'name', timeprogram, 50, 55, HeatingMode.AUTO)
        system = System(holiday_mode, None, [], [], hot_water, None, 5, None, [])

        active_mode = system.get_active_mode_hot_water()

        self.assertEqual(QuickMode.QM_HOLIDAY, active_mode.current_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_zone(self):
        with open(TestUtil.path('files/responses/zone_always_on'), 'r') as file:
            raw_zone = json.loads(file.read())

        zone = Mapper.zone(raw_zone)
        system = System(None, None, [zone], None, None, None, 5, None, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertEqual(HeatingMode.DAY, active_mode.sub_mode)
        self.assertEqual(20, active_mode.target_temperature)

    def test_get_active_mode_zone_off(self):
        with open(TestUtil.path('files/responses/zone_always_off'), 'r') as file:
            raw_zone = json.loads(file.read())

        zone = Mapper.zone(raw_zone)
        system = System(None, None, [zone], None, None, None, 5, None, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertEqual(HeatingMode.NIGHT, active_mode.sub_mode)
        self.assertEqual(19.5, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_veto(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)
        quickveto = QuickVeto(0, 55)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, quickveto, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, None, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(HeatingMode.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(quickveto.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_holiday_mode(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)
        holiday_mode = HolidayMode(True, datetime.date.today(), datetime.date.today(), 10)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(holiday_mode, None, [zone], None, None, None, 5, None, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickMode.QM_HOLIDAY, active_mode.current_mode)
        self.assertEqual(holiday_mode.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_water_boost(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, QuickMode.QM_HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertEqual(timeprogram_day_setting.mode, active_mode.sub_mode)
        self.assertEqual(timeprogram_day_setting.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_system_off(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, QuickMode.QM_SYSTEM_OFF, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickMode.QM_SYSTEM_OFF, active_mode.current_mode)
        self.assertEqual(Zone.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_one_day_home(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day_setting_sunday = TimeProgramDaySetting('00:00', 25, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': TimeProgramDay([timeprogram_day_setting_sunday]),
        }
        timeprogram = TimeProgram(timeprogram_days)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, QuickMode.QM_ONE_DAY_AT_HOME, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickMode.QM_ONE_DAY_AT_HOME, active_mode.current_mode)
        self.assertEqual(timeprogram_day_setting_sunday.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_one_day_away(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, QuickMode.QM_ONE_DAY_AWAY, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickMode.QM_ONE_DAY_AWAY, active_mode.current_mode)
        self.assertEqual(zone.target_min_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_party(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, QuickMode.QM_PARTY, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickMode.QM_PARTY, active_mode.current_mode)
        self.assertEqual(zone.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_quick_veto(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        quick_veto = QuickVeto(0, 15)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, quick_veto, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, None, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(HeatingMode.QUICK_VETO, active_mode.current_mode)
        self.assertEqual(zone.quick_veto.target_temperature, active_mode.target_temperature)

    def test_get_active_mode_zone_quick_mode_ventilation(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', 20, HeatingMode.DAY)
        timeprogram_day_setting_sunday = TimeProgramDaySetting('00:00', 25, HeatingMode.DAY)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': TimeProgramDay([timeprogram_day_setting_sunday]),
        }
        timeprogram = TimeProgram(timeprogram_days)

        zone = Zone('1', 'Test', timeprogram, 20, 20, HeatingMode.AUTO, None, 18, 'STANDBY', False)
        system = System(None, None, [zone], None, None, None, 5, QuickMode.QM_VENTILATION_BOOST, [])

        active_mode = system.get_active_mode_zone(zone)

        self.assertEqual(QuickMode.QM_VENTILATION_BOOST, active_mode.current_mode)
        self.assertEqual(Zone.MIN_TEMP, active_mode.target_temperature)

    def test_get_active_mode_circulation_hot_water_boost(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', None, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        circulation = Circulation('id', 'name', timeprogram, HeatingMode.AUTO)
        system = System(None, None, [], None, None, circulation, 5, QuickMode.QM_HOTWATER_BOOST, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickMode.QM_HOTWATER_BOOST, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_circulation_off(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', None, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        circulation = Circulation('id', 'name', timeprogram, HeatingMode.AUTO)
        system = System(None, None, [], None, None, circulation, 5, QuickMode.QM_SYSTEM_OFF, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickMode.QM_SYSTEM_OFF, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_circulation_holiday(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', None, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        circulation = Circulation('id', 'name', timeprogram, HeatingMode.AUTO)
        holiday_mode = HolidayMode(True, datetime.date.today(), datetime.date.today(), 10)
        system = System(holiday_mode, None, [], None, None, circulation, 5, None, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(QuickMode.QM_HOLIDAY, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_circulation_auto(self):
        timeprogram_day_setting = TimeProgramDaySetting('00:00', None, HeatingMode.ON)
        timeprogram_day = TimeProgramDay([timeprogram_day_setting])
        timeprogram_days = {
            'monday': timeprogram_day,
            'tuesday': timeprogram_day,
            'wednesday': timeprogram_day,
            'thursday': timeprogram_day,
            'friday': timeprogram_day,
            'saturday': timeprogram_day,
            'sunday': timeprogram_day,
        }
        timeprogram = TimeProgram(timeprogram_days)

        circulation = Circulation('id', 'name', timeprogram, HeatingMode.AUTO)
        system = System(None, None, [], None, None, circulation, 5, None, [])

        active_mode = system.get_active_mode_circulation()

        self.assertEqual(HeatingMode.AUTO, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertEqual(HeatingMode.ON, active_mode.sub_mode)

    def test_room_handling_with_rooms(self):
        r1 = Room(10, "name1", None, None, None, None, None, False, False, [])
        r2 = Room(11, "name1", None, None, None, None, None, False, False, [])
        system = System(None, None, [], [r1, r2], None, None, 5, None, [])

        self.assertEqual(2, len(system.rooms))
        self.assertEqual(r1, system.get_room(10))
        self.assertEqual(r2, system.get_room(11))

    def test_room_handling_with_no_rooms(self):
        system = System(None, None, [], [], None, None, 5, None, [])

        self.assertEqual(0, len(system.rooms))
        self.assertEqual(0, len(system._rooms_dict))

    def test_zone_handling_with_zones(self):
        z1 = Zone("id1", "name1", None, None, None, None, None, None, None, None)
        z2 = Zone("id2", "name1", None, None, None, None, None, None, None, None)
        system = System(None, None, [z1, z2], [], None, None, 5, None, [])

        self.assertEqual(2, len(system.zones))
        self.assertEqual(z1, system.get_zone("id1"))
        self.assertEqual(z2, system.get_zone("id2"))

    def test_zone_handling_with_no_zones(self):
        system = System(None, None, [], [], None, None, 5, None, [])

        self.assertEqual(0, len(system.zones))
        self.assertEqual(0, len(system._zones_dict))

    def test_set_zone_existing_zone(self):
        z1 = Zone("id1", "name1", None, None, None, None, None, None, None, None)
        z2 = Zone("id2", "name1", None, None, None, None, None, None, None, None)
        z3 = Zone("id2", "name3", None, None, None, None, None, None, None, None)
        system = System(None, None, [z1, z2], [], None, None, 5, None, [])

        system.set_zone(z2.id, z3)
        self.assertEqual(2, len(system.zones))
        self.assertEqual(z3, system.get_zone(z2.id))

    def test_set_zone_new_zone(self):
        z1 = Zone("id1", "name1", None, None, None, None, None, None, None, None)
        z2 = Zone("id2", "name1", None, None, None, None, None, None, None, None)
        z3 = Zone("id3", "name3", None, None, None, None, None, None, None, None)
        system = System(None, None, [z1, z2], [], None, None, 5, None, [])

        self.assertEqual(2, len(system.zones))
        system.set_zone(z3.id, z3)
        self.assertEqual(3, len(system.zones))

    def test_set_room_existing_room(self):
        r1 = Room(10, "name1", None, None, None, None, None, False, False, [])
        r2 = Room(11, "name1", None, None, None, None, None, False, False, [])
        r3 = Room(11, "name3", None, None, None, None, None, False, False, [])
        system = System(None, None, [], [r1, r2], None, None, 5, None, [])

        system.set_room(r3.id, r3)
        self.assertEqual(2, len(system.rooms))
        self.assertEqual(r3, system.get_room(r2.id))

    def test_set_room_new_room(self):
        r1 = Room(10, "name1", None, None, None, None, None, False, False, [])
        r2 = Room(11, "name1", None, None, None, None, None, False, False, [])
        r3 = Room(12, "name3", None, None, None, None, None, False, False, [])
        system = System(None, None, [], [r1, r2], None, None, 5, None, [])

        system.set_room(r3.id, r3)
        self.assertEqual(3, len(system.rooms))


if __name__ == '__main__':
    unittest.main()
