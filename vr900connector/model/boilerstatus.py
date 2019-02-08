from datetime import datetime


class BoilerStatus:
    deviceName: str = None
    code: str = None
    title: str = None
    description: str = None
    hint: str = None
    lastUpdate: datetime = None
    currentTemperature: float = None
    waterPressure: float = None
    waterPressureUnit: str = None
