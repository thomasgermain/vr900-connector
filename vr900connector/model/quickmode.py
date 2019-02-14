from . import BoostMode


class QuickMode:
    boostMode = None
    remainingDuration = 0

    def __init__(self, name, remaining_duration):
        self.boostMode = BoostMode.from_name(name)
        self.remainingDuration = remaining_duration
