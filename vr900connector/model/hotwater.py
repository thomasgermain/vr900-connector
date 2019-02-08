import copy

from .constant import HOT_WATER_MODE_OFF, QM_HOTWATER_BOOST, HOT_WATER_MODE_ON, \
    HOT_WATER_MODE_AUTO_OFF, HOT_WATER_MIN_TEMP, HOT_WATER_MODE_AUTO_ON
from . import Component


class HotWater(Component):

    def get_current_time_program(self):
        """There is no quick veto for hot water"""
        if self.operationMode == HOT_WATER_MODE_ON:
            return TimeProgramDaySetting(str(0), self.targetTemperature, HOT_WATER_MODE_ON)
        elif self.operationMode == HOT_WATER_MODE_OFF:
            return TimeProgramDaySetting(str(0), HOT_WATER_MIN_TEMP, HOT_WATER_MODE_OFF)
        elif self.operationMode == QM_HOTWATER_BOOST:
            return TimeProgramDaySetting(str(0), self.targetTemperature, QM_HOTWATER_BOOST)
        else:
            # Mode AUTO
            mode = copy.deepcopy(super().get_current_time_program())
            if mode.mode == HOT_WATER_MODE_ON:
                mode.mode = HOT_WATER_MODE_AUTO_ON
                mode.temperature = self.targetTemperature
            else:
                mode.mode = HOT_WATER_MODE_AUTO_OFF
                mode.temperature = HOT_WATER_MIN_TEMP
            return mode
