import copy
from typing import List

from .constant import THERMOSTAT_ZONE_MODE_OFF, THERMOSTAT_ROOM_MODE_MANUAL, FROST_PROTECTION_TEMP, \
    THERMOSTAT_ZONE_MODE_DAY
from . import Component, Room


class Zone(Component):
    targetMinTemperature: float = None
    activeFunction: str = None
    rooms: List[Room] = []
    rbr: bool = False

    def get_current_time_program(self):
        mode = copy.deepcopy(super().get_current_time_program())
        if self.quickVeto is None:
            if self.operationMode == THERMOSTAT_ZONE_MODE_OFF:
                mode = TimeProgramDaySetting(str(0), FROST_PROTECTION_TEMP, THERMOSTAT_ZONE_MODE_OFF)
            elif mode.mode == THERMOSTAT_ROOM_MODE_MANUAL:
                mode.temperature = self.targetTemperature
            elif mode.mode == THERMOSTAT_ZONE_MODE_DAY:
                mode.temperature = self.targetTemperature
            else:
                mode.temperature = self.targetMinTemperature
        return mode