from typing import List

from . import Component, TimeProgram, QuickVeto, Device, ActiveMode, HeatingMode, Constants


class Room(Component):
    """
    This class represents a Room, which is typically a group of VR50/VR51

    Args:
        child_lock: Are all VR50 locked ? (It means you cannot change temperature using the VR50 directly)
        window_open: Set to True when the system detect temperature drop
        devices: List of devices in the room, see :class:`vr900connector.Device`
    """

    MODES = [HeatingMode.OFF, HeatingMode.MANUAL, HeatingMode.AUTO, HeatingMode.QUICK_VETO]
    """
    List of available modes for a room
    """

    MIN_TEMP = Constants.FROST_PROTECTION_TEMP
    """
    Minimum temperature in celsius for a room, this is coming from documentation
    """

    MAX_TEMP = Constants.THERMOSTAT_MAX_TEMP
    """
    Maximum temperature celsius for a room, this is coming from my tests with android application, cannot go above 30
    """

    def __init__(self, component_id: any, name: str, time_program: TimeProgram, current_temperature: float,
                 target_temperature: float, operation_mode: HeatingMode, quick_veto: QuickVeto, child_lock: bool,
                 window_open: bool, devices: List[Device]):
        super().__init__(component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                         quick_veto)
        self.child_lock = child_lock
        self.window_open = window_open
        self.devices = devices

    def _get_specific_active_mode(self) -> ActiveMode:
        if self.operation_mode == HeatingMode.OFF:
            mode = ActiveMode(self.MIN_TEMP, HeatingMode.OFF)
        else:  # MODE_MANUAL
            mode = ActiveMode(self.target_temperature, HeatingMode.MANUAL)

        return mode
