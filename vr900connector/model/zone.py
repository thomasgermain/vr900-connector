import copy

from . import Component
from .timeprogram import TimeProgramDaySetting
from .constant import THERMOSTAT_ZONE_MODE_OFF, THERMOSTAT_ROOM_MODE_MANUAL, FROST_PROTECTION_TEMP, \
    THERMOSTAT_ZONE_MODE_DAY


class Zone(Component):
    targetMinTemperature = None
    activeFunction = None
    rooms = []
    rbr = False

    def get_current_time_program(self):
        mode = copy.deepcopy(Component.get_current_time_program(self))
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
