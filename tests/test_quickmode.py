import unittest

from vr900connector.model import QuickMode


class QuickModeTest(unittest.TestCase):

    def test_for_zone(self):
        values = QuickMode.for_zone()
        self.assertEqual(5, len(values))

    def test_for_room(self):
        values = QuickMode.for_room()
        self.assertEqual(2, len(values))

    def test_for_hot_water(self):
        values = QuickMode.for_hot_water()
        self.assertEqual(3, len(values))

    def test_for_circulation(self):
        values = QuickMode.for_circulation()
        self.assertEqual(3, len(values))
