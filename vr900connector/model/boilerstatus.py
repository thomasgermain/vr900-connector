from datetime import datetime


class BoilerStatus:
    """
    Represents the status of the boiler

    Args:
        device_name: name of the boiler
        description: long description of the code
        title: short description of the code
        code: code representing the current status of the boiler (heating, off, error, etc.)
        hint: hint (provided by the API)
        last_update: last update of the status (provided by the API)
    """

    def __init__(self, device_name: str, description: str, title: str, code: str, hint: str, last_update: datetime,
                 online_status: str, update_status: str, water_pressure: float, current_temperature: float):
        self.device_name = device_name
        self.description = description
        self.title = title
        self.code = code
        self.hint = hint
        self.last_update = last_update
        self.online_status = online_status
        self.update_status = update_status
        self.water_pressure = water_pressure
        self.current_temperature = current_temperature

    @property
    def is_error(self) -> bool:
        return self.code and (self.code.startswith('F') or self.code == 'con')

    @property
    def is_online(self):
        return self.online_status == 'ONLINE'

    @property
    def is_up_to_date(self):
        return self.update_status == 'UPDATE_NOT_PENDING'

