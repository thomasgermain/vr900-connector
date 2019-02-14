class QuickVeto:
    remainingTime = 0
    targetTemperature = None

    def __init__(self, remaining_time, target_temperature):
        self.remainingTime = remaining_time
        self.targetTemperature = target_temperature
