import unittest

from vr900connector.model import Circulation, HeatingMode


class CirculationTest(unittest.TestCase):

    def test_get_active_mode_on(self):
        circulation = Circulation('id', 'Test', None, HeatingMode.ON)

        active_mode = circulation.active_mode

        self.assertEqual(HeatingMode.ON, active_mode.current_mode)
        self.assertIsNone(active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)


if __name__ == '__main__':
    unittest.main()
