class HolidayMode:
    """
    Represents system's holiday mode

    Args:
        active: If holiday mode is active
        start_date: Start date of the holiday mode
        end_date: End date of the holiday mode
        target_temperature: Target temperature during holiday mode
    """

    def __init__(self, active, start_date, end_date, target_temperature):
        self.active = active
        self.start_date = start_date
        self.end_date = end_date
        self.target_temperature = target_temperature



