from datetime import date

from vr900connector.model import ActiveMode, QuickMode


class HolidayMode:
    """
    Represents system's holiday mode

    Args:
        active: If holiday mode is active
        start_date: Start date of the holiday mode
        end_date: End date of the holiday mode
        target_temperature: Target temperature during holiday mode
    """

    def __init__(self, active: bool, start_date: date, end_date: date, target_temperature: float):
        self.active = active
        self.start_date = start_date
        self.end_date = end_date
        self.target_temperature = target_temperature

    @property
    def active_mode(self) -> ActiveMode:
        if self.active:
            return ActiveMode(self.target_temperature, QuickMode.HOLIDAY)
