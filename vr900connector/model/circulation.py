from . import Component, TimeProgram
from .constants import MODE_ON, MODE_OFF, MODE_AUTO


class Circulation(Component):
    """
    Circulation is quite a special component since there is no temperature nor quick veto involved.
    This class only exists to have a clean hierarchy
    """

    MODES = [MODE_ON, MODE_OFF, MODE_AUTO]
    """
    List of mode available for circulation
    """

    def __init__(self, component_id: any, name: str, time_program: TimeProgram, operation_mode: str):
        super().__init__(component_id, name, time_program, None, None, operation_mode, None)
