from datetime import date


class HolidayMode:
    active: bool = False
    startDate: date = None
    endDate: date = None
    targetTemperature: float = None
