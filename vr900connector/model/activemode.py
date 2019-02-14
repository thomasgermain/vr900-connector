class ActiveMode:
    targetTemperature = None
    name = None
    sub_mode = None

    def __init__(self, target_temperature, name, sub_mode=None):
        self.targetTemperature = target_temperature
        self.name = name
        self.sub_mode = sub_mode
