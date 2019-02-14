import copy

from .component import Component
from .constant import CIRCULATION_MODE_ON, CIRCULATION_MODE_AUTO_ON, CIRCULATION_MODE_AUTO_OFF


class Circulation(Component):

    def get_current_time_program(self):
        """There is no quick veto for circulation"""
        mode = copy.deepcopy(super().get_current_time_program())
        if mode.mode == CIRCULATION_MODE_ON:
            mode.mode = CIRCULATION_MODE_AUTO_ON
        else:
            mode.mode = CIRCULATION_MODE_AUTO_OFF
        return mode
