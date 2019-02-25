from .component import Component
from .timeprogram import TimeProgramDaySetting
from .constants import MODE_ON, MODE_AUTO, MODE_OFF, QM_HOTWATER_BOOST


class HotWater(Component):
    """
    This class represents the hot water of your system
    """

    MODES = [MODE_ON, MODE_OFF, MODE_AUTO, QM_HOTWATER_BOOST]
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

    def __init__(self, component_id, name, time_program, current_temperature, target_temperature, operation_mode):
        super().__init__(component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                         None)

    def get_current_time_program(self):
        # There is no quick veto for hot water, and quick mode is taking precedence over timeprogram
        if self.operation_mode == QM_HOTWATER_BOOST:
            return TimeProgramDaySetting(str(0), self.target_temperature, QM_HOTWATER_BOOST)
        else:
            return super().get_current_time_program()
