import unittest
from datetime import datetime

from vr900connector.model import TimeProgramDaySetting, TimeProgramDay, TimeProgram, HeatingMode


class TimeProgramTest(unittest.TestCase):

    def test_time_program_simple(self):
        tpds1 = TimeProgramDaySetting('00:00', 25, HeatingMode.ON)
        tpds2 = TimeProgramDaySetting('02:00', 20, HeatingMode.OFF)

        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({'monday': monday, 'sunday': TimeProgramDay([])})

        current = timeprogram.get_time_program_for(datetime(2019, 2, 18, 1, 0))
        self._assert(tpds1, current)

    def test_time_program_after_last(self):
        tpds1 = TimeProgramDaySetting('00:00', 25, HeatingMode.ON)
        tpds2 = TimeProgramDaySetting('02:00', 20, HeatingMode.OFF)

        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({'monday': monday, 'sunday': TimeProgramDay([])})

        current = timeprogram.get_time_program_for(datetime(2019, 2, 18, 3, 0))
        self._assert(tpds2, current)

    def test_time_program_before_first(self):
        tpds1 = TimeProgramDaySetting('01:00', 25, HeatingMode.ON)
        tpds2 = TimeProgramDaySetting('02:00', 20, HeatingMode.OFF)

        tpds_sunday = TimeProgramDaySetting('15:00', 15, HeatingMode.OFF)

        sunday = TimeProgramDay([tpds_sunday])
        monday = TimeProgramDay([tpds1, tpds2])

        timeprogram = TimeProgram({'monday': monday, 'sunday': sunday})

        current = timeprogram.get_time_program_for(datetime(2019, 2, 18, 0, 30))
        self._assert(tpds_sunday, current)

    def test_wrong_start_time(self):
        self.assertRaises(ValueError, TimeProgramDaySetting, 'xx', 25, 'Test1')

    def _assert(self, expected, actual):
        self.assertEqual(expected.target_temperature, actual.target_temperature)
        self.assertEqual(expected.mode, actual.mode)
        self.assertEqual(expected.start_time, actual.start_time)


if __name__ == '__main__':
    unittest.main()
