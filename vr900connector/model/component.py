from datetime import datetime
from .constants import QUICK_VETO
from .timeprogram import TimeProgramDaySetting


class Component:
    """
    This class represents a component in your installation (room, zone, hot water, circulation).

    Args:
        component_id: id of the component
        name: name of the component (this is the name you defined in the application or on VRC700)
        time_program: The timeprogram you defined, see :class:`vr900connector.model.TimeProgram`
        current_temperature: The current temperature of the component
        target_temperature: The target temperature of the component
        operation_mode: Configured operation mode for the component. It can be completely different from the
        :class:`vr900connector.model.ActiveMode`. To get the real running mode, consider using
        :func:`vr900connector.model.System.get_active_mode_zone()`
        quick_veto: it there is a quick veto running on
    """

    def __init__(self, component_id, name, time_program, current_temperature, target_temperature, operation_mode,
                 quick_veto):
        self.id = component_id
        self.name = name
        self.time_program = time_program
        self.current_temperature = current_temperature
        self.target_temperature = target_temperature
        self.operation_mode = operation_mode
        self.quick_veto = quick_veto

    def get_current_time_program(self):
        """
        :return: The :class:`vr900connector.model.TimeProgramDaySetting` based on datetime.now() or quick veto
        if quick veto is running on
        """
        if self.quick_veto:
            return TimeProgramDaySetting(str(self.quick_veto.remaining_time), self.quick_veto.target_temperature, QUICK_VETO)

        return self.time_program.get_time_program_for(datetime.now())
