import unittest

from vr900connector.model import Zone, HeatingMode


class ZoneTest(unittest.TestCase):

    def test_get_active_mode_night(self):
        zone = Zone('id', 'Test', None, 10.0, 7.0, HeatingMode.NIGHT, None, 6.0, 'Heating', False)

        active_mode = zone.active_mode

        self.assertEqual(HeatingMode.NIGHT, active_mode.current_mode)
        self.assertEqual(6.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_day(self):
        zone = Zone('id', 'Test', None, 10.0, 7.0, HeatingMode.DAY, None, 6.0, 'Heating', False)

        active_mode = zone.active_mode

        self.assertEqual(HeatingMode.DAY, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self):
        zone = Zone('id', 'Test', None, 10.0, 7.0, HeatingMode.OFF, None, 6.0, 'Heating', False)

        active_mode = zone.active_mode

        self.assertEqual(HeatingMode.OFF, active_mode.current_mode)
        self.assertEqual(Zone.MIN_TEMP, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)


if __name__ == '__main__':
    unittest.main()
