class ActiveMode:
    """
    Represents the active mode for a :class:`vr900connector.model.Component`.

    Active mode for a component can ony be retrieve via :class:`vr900connector.SystemManager` since it can be quite
    complex (quick veto, quick mode, holiday mode, etc.)

    Args:
        target_temperature: The target temperature the component is trying to reach
        name: Name of the current mode, list is available at :mod:`vr900connector.model.constants`
    """

    def __init__(self, target_temperature: float, name: str):
        self.target_temperature = target_temperature
        self.name = name
