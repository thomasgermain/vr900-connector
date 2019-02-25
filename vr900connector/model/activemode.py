from . import Mode


class ActiveMode:
    """
    Represents the active mode for a :class:`vr900connector.model.Component`.

    Active mode for a component can ony be retrieve via :class:`vr900connector.SystemManager` since it can be quite
    complex (quick veto, quick mode, holiday mode, etc.)

    Args:
        target_temperature: The target temperature the component is trying to reach
        current_mode: Name of the current mode, list is available at :mod:`vr900connector.model.constants`
        sub_mode: Name of the sub mode (available when current_mode is 'AUTO' and active mode is not related to a Room),
        otherwise it will be None
    """

    def __init__(self, target_temperature: float, current_mode: Mode, sub_mode: Mode = None):
        self.target_temperature = target_temperature
        self.current_mode = current_mode
        self.sub_mode = sub_mode
