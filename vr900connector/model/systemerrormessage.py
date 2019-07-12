import datetime


class SystemErrorMessage:

    def __init__(self, device_name: str, title: str, status_code: str, description: str, timestamp: datetime):
        self.device_name = device_name
        self.title = title
        self.status_code = status_code
        self.description = description
        self.timestamp = timestamp
