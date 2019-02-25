from datetime import datetime
import abc

from . import TimeProgram, QuickVeto, ActiveMode, HeatingMode


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

    def __init__(self, component_id: any, name: str, time_program: TimeProgram, current_temperature: float,
                 target_temperature: float, operation_mode: HeatingMode, quick_veto: QuickVeto):
        self.id = component_id
        self.name = name
        self.time_program = time_program
        self.current_temperature = current_temperature
        self.target_temperature = target_temperature
        self.operation_mode = operation_mode
        self.quick_veto = quick_veto

    @property
    def active_mode(self) -> ActiveMode:
        """
        Get the active mode for a component. Please note that a component is not aware of quick mode or holiday mode

        :return: ActiveMode
        """

        if self.quick_veto:
            return ActiveMode(self.quick_veto.target_temperature, HeatingMode.QUICK_VETO)

        if self.operation_mode == HeatingMode.AUTO:
            setting = self.time_program.get_time_program_for(datetime.now())
            return ActiveMode(setting.target_temperature, HeatingMode.AUTO, setting.mode)
        else:
            return self._get_specific_active_mode()

    @abc.abstractmethod
    def _get_specific_active_mode(self) -> ActiveMode:
        """
        Get active mode for specific mode other than 'AUTO'

        :return: ActiveMode
        """
