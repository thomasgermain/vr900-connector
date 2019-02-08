from . import BoostMode


class QuickMode:
    boostMode: BoostMode = None
    remainingDuration: int = 0

    def __init__(self, name: str, remaining_duration: int):
        self.boostMode = BoostMode.from_name(name)
        self.remainingDuration = remaining_duration
