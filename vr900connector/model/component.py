from datetime import datetime

from .timeprogram import TimeProgramDaySetting
from .constant import THERMOSTAT_QUICK_VETO


class Component:
    id = None
    name = None
    timeProgram = None
    currentTemperature = None
    targetTemperature = None
    operationMode = None
    quickVeto = None

    def get_current_time_program(self):
        if self.quickVeto:
            return TimeProgramDaySetting('0',
                                         self.quickVeto.targetTemperature, THERMOSTAT_QUICK_VETO)

        return self.timeProgram.get_current_time_program(datetime.now())
