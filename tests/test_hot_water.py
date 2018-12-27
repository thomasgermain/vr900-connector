import unittest

from vr900connector.model import HotWater, HeatingMode


class HotWaterTest(unittest.TestCase):

    def test_get_active_mode_on(self):
        hot_water = HotWater('id', 'Test', None, 5.0, 7.0, HeatingMode.ON)

        active_mode = hot_water.active_mode

        self.assertEqual(HeatingMode.ON, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self):
        hot_water = HotWater('id', 'Test', None, 5.0, 7.0, HeatingMode.OFF)

        active_mode = hot_water.active_mode

        self.assertEqual(HeatingMode.OFF, active_mode.current_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)


if __name__ == '__main__':
    unittest.main()
