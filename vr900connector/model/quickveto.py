class QuickVeto:
    """
    This represents a quick veto which can be applied for a :class:`vr900connector.model.Room` or a
    :class:`vr900connector.model.Zone` only.

    For a room, quick veto duration is customizable and it's possible to get the remaining duration.

    For a zone, quick veto duration is NOT customizable and the API returns always '0' as remaining duration

    Args:
        remaining_time: The remaining time of the quick veto or 0 if not available
        target_temperature: Target temperature of the quick veto
    """

    def __init__(self, remaining_time, target_temperature):
        self.remaining_time = remaining_time
        self.target_temperature = target_temperature
