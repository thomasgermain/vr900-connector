from . import Component
from .timeprogram import TimeProgramDaySetting
from .constants import FROST_PROTECTION_TEMP, MODE_OFF, MODE_MANUAL, MODE_AUTO, QUICK_VETO, THERMOSTAT_MAX_TEMP


class Room(Component):
    """
    This class represents a Room, which is typically a group of VR50/VR51

    Args:
        child_lock: Are all VR50 locked ? (It means you cannot change temperature using the VR50 directly)
        window_open: Set to True when the system detect temperature drop
        devices: List of devices in the room, see :class:`vr900connector.Device`
    """

    MODES = [MODE_OFF, MODE_MANUAL, MODE_AUTO, QUICK_VETO]
    """
    List of available modes for a room
    """

    MIN_TEMP = FROST_PROTECTION_TEMP
    """
    Minimum temperature in celsius for a room, this is coming from documentation
    """

    MAX_TEMP = THERMOSTAT_MAX_TEMP
    """
    Maximum temperature celsius for a room, this is coming from my tests with android application, cannot go above 30
    """

    def __init__(self, component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                 quick_veto, child_lock, window_open, devices):
        super().__init__(component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                         quick_veto)
        self.child_lock = child_lock
        self.window_open = window_open
        self.devices = devices

    def get_current_time_program(self):
        mode = None
        if not self.quick_veto:
            if self.operation_mode == MODE_OFF:
                mode = TimeProgramDaySetting(str(0), self.MIN_TEMP, MODE_OFF)
            elif self.operation_mode == MODE_MANUAL:
                mode = TimeProgramDaySetting(str(0), self.target_temperature, MODE_MANUAL)

        # Auto or quick veto, handled by parent
        if not mode:
            mode = super().get_current_time_program()
            if not mode.mode:
                mode.mode = MODE_AUTO

        return mode
