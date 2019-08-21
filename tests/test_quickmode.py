"""Test for quick mode."""
import unittest

from vr900connector.model import QuickMode


class QuickModeTest(unittest.TestCase):
    """Test class."""

    def test_for_zone(self) -> None:
        """Test get quick mode for zone."""
        values = QuickMode.get_for_zone()
        self.assertEqual(6, len(values))

    def test_for_room(self) -> None:
        """Test get quick mode for zone."""
        values = QuickMode.get_for_room()
        self.assertEqual(2, len(values))

    def test_for_hot_water(self) -> None:
        """Test get quick mode for zone."""
        values = QuickMode.get_for_hot_water()
        self.assertEqual(4, len(values))

    def test_for_circulation(self) -> None:
        """Test get quick mode for zone."""
        values = QuickMode.get_for_circulation()
        self.assertEqual(4, len(values))
