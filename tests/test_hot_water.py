"""Test for hot water."""
import unittest

from tests import testutil
from vr900connector.model import HotWater, OperationMode


class HotWaterTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_on(self) -> None:
        """Test active mode on."""
        hot_water = HotWater('id', 'Test', testutil.default_time_program(),
                             5.0, 7.0, OperationMode.ON)

        active_mode = hot_water.active_mode

        self.assertEqual(OperationMode.ON, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self) -> None:
        """Test active mode off."""
        hot_water = HotWater('id', 'Test', testutil.default_time_program(),
                             5.0, 7.0, OperationMode.OFF)

        active_mode = hot_water.active_mode

        self.assertEqual(OperationMode.OFF, active_mode.current_mode)
        self.assertEqual(HotWater.MIN_TEMP, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)
