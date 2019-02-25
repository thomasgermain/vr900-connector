from .component import Component
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

    def __init__(self, component_id, name, time_program, operation_mode):
        super().__init__(component_id, name, time_program, None, None, operation_mode, None)
