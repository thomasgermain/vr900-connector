from datetime import datetime

from . import Component, TimeProgram, ActiveMode, HeatingMode


class Circulation(Component):
    """
    Circulation is quite a special component since there is no temperature nor quick veto involved.
    This class only exists to have a clean hierarchy
    """

    MODES = [HeatingMode.ON, HeatingMode.OFF, HeatingMode.AUTO]
    """
    List of mode available for circulation
    """

    def __init__(self, component_id: any, name: str, time_program: TimeProgram, operation_mode: HeatingMode):
        super().__init__(component_id, name, time_program, None, None, operation_mode, None)

    def _get_specific_active_mode(self) -> ActiveMode:
        if self.operation_mode == HeatingMode.AUTO:
            setting = self.time_program.get_time_program_for(datetime.now())
            mode = ActiveMode(None, HeatingMode.AUTO, setting.mode)
        else:
            mode = ActiveMode(None, self.operation_mode)
        return mode
