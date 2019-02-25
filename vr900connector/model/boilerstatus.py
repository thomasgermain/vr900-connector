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

    def __init__(self, device_name: str, description: str, title: str, code: str, hint: str, last_update: datetime):
        self.device_name = device_name
        self.description = description
        self.title = title
        self.code = code
        self.hint = hint
        self.last_update = last_update
