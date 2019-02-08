import copy
from typing import List

from . import Component, Device, TimeProgramDaySetting
from .constant import FROST_PROTECTION_TEMP, THERMOSTAT_ROOM_MODE_OFF, \
    THERMOSTAT_ROOM_MODE_MANUAL, THERMOSTAT_ROOM_MODE_AUTO_OFF, THERMOSTAT_ROOM_MODE_AUTO_ON


class Room(Component):
    childLock: bool = False
    isWindowOpen: bool = False
    devices: List[Device] = []

    def get_current_time_program(self):
        mode = copy.deepcopy(super().get_current_time_program())
        if self.quickVeto is None:
            if self.operationMode == THERMOSTAT_ROOM_MODE_OFF:
                mode = TimeProgramDaySetting(str(0), FROST_PROTECTION_TEMP, THERMOSTAT_ROOM_MODE_OFF)
            elif mode.mode == THERMOSTAT_ROOM_MODE_MANUAL:
                mode.temperature = self.targetTemperature
            else:
                if mode.temperature >= self.targetTemperature:
                    mode.mode = THERMOSTAT_ROOM_MODE_AUTO_OFF
                else:
                    mode.mode = THERMOSTAT_ROOM_MODE_AUTO_ON
        return mode
