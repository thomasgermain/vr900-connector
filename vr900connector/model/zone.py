import copy

from . import Component, TimeProgram, TimeProgramDaySetting, QuickVeto
from .constants import FROST_PROTECTION_TEMP, MODE_OFF, MODE_AUTO, QUICK_VETO, THERMOSTAT_MAX_TEMP, MODE_DAY, MODE_NIGHT


class Zone(Component):
    """
    This class represents a zone (configured with the VR700).

    If rbr (Room By Room) is True, the zone itself doesn't mean anything anymore, rooms are 'controlling' the zone.

    Args:
        target_min_temperature: Minimal temperature to reach
        active_function: Active function for the zone, basically, 'HEATING' or STAND BY'
        rbr: Set to True if the zone is controlled by rooms
    """

    MODES: list = [MODE_AUTO, MODE_OFF, MODE_DAY, MODE_NIGHT, QUICK_VETO]
    """
    List of available modes for a zone
    """

    MIN_TEMP: float = FROST_PROTECTION_TEMP
    """
    Minimum temperature in celsius for a room, this is coming from documentation
    """

    MAX_TEMP: float = THERMOSTAT_MAX_TEMP
    """
    Maximum temperature celsius for a room, this is coming from my tests with android application, cannot go above 30
    """

    def __init__(self, component_id: any, name: str, time_program: TimeProgram, current_temperature: float,
                 target_temperature: float, operation_mode: str, quick_veto: QuickVeto, target_min_temperature: float,
                 active_function: str, rbr: bool):
        super().__init__(component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                         quick_veto)
        self.target_min_temperature = target_min_temperature
        self.active_function = active_function
        self.rbr = rbr

    def get_current_time_program(self) -> TimeProgramDaySetting:
        mode = copy.deepcopy(Component.get_current_time_program(self))
        if self.quick_veto is None:
            if self.operation_mode == MODE_OFF:
                mode = TimeProgramDaySetting(str(0), self.MIN_TEMP, MODE_OFF)
            elif self.operation_mode == MODE_DAY:
                mode = TimeProgramDaySetting(str(0), self.target_temperature, MODE_DAY)
            elif self.operation_mode == MODE_NIGHT:
                mode = TimeProgramDaySetting(str(0), self.target_min_temperature, MODE_NIGHT)
            else:
                # Auto or quick veto is handled by parent
                mode = super().get_current_time_program()

        return mode
