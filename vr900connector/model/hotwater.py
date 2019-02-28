from . import TimeProgram, Component, ActiveMode
from .constants import MODE_ON, MODE_AUTO, MODE_OFF


class HotWater(Component):
    """
    This class represents the hot water of your system
    """

    MODES = [MODE_ON, MODE_OFF, MODE_AUTO]
    """
    List of modes available for hot water
    """

    MIN_TEMP = 35
    """
    Minimum temperature in celsius for the hot water, this is coming from documentation
    """

    MAX_TEMP = 70
    """
    Maximum temperature celsius for the hot water, this is coming from my tests with android application, 
    cannot go above 70
    """

    def __init__(self, component_id: any, name: str, time_program: TimeProgram, current_temperature: float,
                 target_temperature: float, operation_mode: str):
        super().__init__(component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                         None)

    def _get_specific_active_mode(self) -> ActiveMode:
        if self.operation_mode == MODE_ON:
            mode = ActiveMode(self.target_temperature, MODE_ON)
        else:  # MODE_OFF
            mode = ActiveMode(HotWater.MIN_TEMP, MODE_OFF)

        return mode
