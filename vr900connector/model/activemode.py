class ActiveMode:
    targetTemperature: float = None
    name: str = None
    sub_mode: str = None

    def __init__(self, target_temperature: float, name: str, sub_mode: str = None):
        self.targetTemperature = target_temperature
        self.name = name
        self.sub_mode = sub_mode
