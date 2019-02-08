from datetime import datetime

from .constant import THERMOSTAT_QUICK_VETO
from . import TimeProgram, TimeProgramDaySetting, QuickVeto


class Component:
    id: str = None
    name: str = None
    timeProgram: TimeProgram = None
    currentTemperature: float = None
    targetTemperature: float = None
    operationMode: str = None
    quickVeto: QuickVeto = None

    def get_current_time_program(self):
        if self.quickVeto:
            return TimeProgramDaySetting('0',
                                         self.quickVeto.targetTemperature, THERMOSTAT_QUICK_VETO)

        return self.timeProgram.get_current_time_program(datetime.now())
