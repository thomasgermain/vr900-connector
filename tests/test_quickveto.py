import unittest

from vr900connector.model import QuickVeto


class QuickVetoTest(unittest.TestCase):

    def test_wrong_quick_veto(self):
        self.assertRaises(ValueError, QuickVeto, 800000, 15)

    def test_quick_veto(self):
        quickveto = QuickVeto(600, 15)
        self.assertEqual(600, quickveto.remaining_time)
        self.assertEqual(15, quickveto.target_temperature)

