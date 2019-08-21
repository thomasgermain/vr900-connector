"""Test for rooms."""
import unittest

from vr900connector.model import Room, OperationMode


class RoomTest(unittest.TestCase):
    """Test class."""

    def test_get_active_mode_manual(self) -> None:
        """Test active mode manual."""
        room = Room('1', 'Test', None, 5.0, 7.0, OperationMode.MANUAL, None,
                    True, False, [])

        active_mode = room.active_mode

        self.assertEqual(OperationMode.MANUAL, active_mode.current_mode)
        self.assertEqual(7.0, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)

    def test_get_active_mode_off(self) -> None:
        """Test active mode off."""
        hot_water = Room('1', 'Test', None, 5.0, 7.0, OperationMode.OFF, None,
                         True, False, [])

        active_mode = hot_water.active_mode

        self.assertEqual(OperationMode.OFF, active_mode.current_mode)
        self.assertEqual(Room.MIN_TEMP, active_mode.target_temperature)
        self.assertIsNone(active_mode.sub_mode)
