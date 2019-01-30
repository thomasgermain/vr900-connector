import json
import unittest

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
        self.assertEqual(constant.WATER_HEATER_MODE_BOOST, quick_mode.name)
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


if __name__ == '__main__':
    unittest.main()
