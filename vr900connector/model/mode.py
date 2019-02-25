from enum import Enum


class Mode:
    pass


class QuickVeto(Mode):
    """
    This represents a quick veto which can be applied for a :class:`vr900connector.model.Room` or a
    :class:`vr900connector.model.Zone` only.

    For a room, quick veto duration is customizable and it's possible to get the remaining duration.

    For a zone, quick veto duration is NOT customizable and the API returns always '0' as remaining duration

    Args:
        remaining_time: The remaining time of the quick veto (in minute) or 0 if not available
        target_temperature: Target temperature of the quick veto
    """

    def __init__(self, remaining_time: int, target_temperature: float):
        if remaining_time > 1440:
            raise ValueError(remaining_time)

        self.remaining_time = remaining_time
        self.target_temperature = target_temperature


class HeatingMode(Mode, Enum):

    def __init__(self, mode_name: str):
        self._mode_name = mode_name

    AUTO = 'AUTO'
    ON = 'ON'
    OFF = 'OFF'
    MANUAL = 'MANUAL'
    DAY = 'DAY'
    NIGHT = 'NIGHT'
    QUICK_VETO = 'QUICK_VETO'


class QuickMode(Mode, Enum):
    """
    Quick modes are mode you can quickly set with the app. Most of the times, quick modes have system wise impact.
    Example: for 'ONE_DAY_AWAY', the quick mode will prevent zones and water heater from heating.

    This is different from quick veto, which will only impact one component.

    Quick mode are taking precedence in case of simultaneous quick veto and quick mode.

    This class is a helper to check what is impacted by a quick mode.

    Note that there is a default duration for quick modes (which can't be changed) but the API always returns '0' as
    remaining duration, so there is no way to know when quick mode will end

    Vaillant documentation link:
    http://elearning.vaillant.com/vrc700/ci/en/documents/uk/infopool/Operating_instructions.pdf

    Args:
        for_zone: does the quick mode apply to a zone ?
        for_room: does the quick mode apply to a room ?
        for_hot_water: does the quick mode apply to the hot_water ?
        for_circulation: does the quick mode apply to the circulation ?
    """

    def __init__(self, mode_name: str, for_zone: bool, for_room: bool, for_hot_water: bool, for_circulation: bool):
        self._mode_name = mode_name
        self.for_zone = for_zone
        self.for_room = for_room
        self.for_hot_water = for_hot_water
        self.for_circulation = for_circulation

    QM_HOTWATER_BOOST = ('QM_HOTWATER_BOOST', False, False, True, True)
    """
    The advanced function heats the water in the domestic hot water cylinder once until the desired DHW circuit 
    temperature set is reached or until you cancel the advanced function early. The heating installation will then 
    return to the pre-set mode
    """

    QM_VENTILATION_BOOST = ('QM_VENTILATION_BOOST', True, False, False, False)
    """
    This advanced function switches the zone off for 30 minutes. The frost protection function is activated, and hot 
    water  generation and circulation remain active. Ventilation is activated and works at the highest ventilation 
    level.
    The advanced function is automatically deactivated after 30 minutes or if you cancel the advanced function early. 
    The heating installation will then return to the pre-set mode
    """

    QM_ONE_DAY_AWAY = ('QM_ONE_DAY_AWAY', True, False, True, True)
    """
    Hot water generation and circulation are switched off and the frost protection is activated. The advanced function 
    is automatically deactivated after 24:00 hours or if you cancel the advanced function first. The heating 
    installation will then return to the pre-set mode. Ventilation is activated and works at the lowest ventilation 
    level.
    """

    QM_SYSTEM_OFF = ('QM_SYSTEM_OFF', True, True, True, True)
    """
    The heating function, hot water circuit and cooling are switched off. The frost protection function is activated.
    The circulation is switched off. Ventilation is activated and works at the lowest ventilation level.
    """

    QM_ONE_DAY_AT_HOME = ('QM_ONE_DAY_AT_HOME', True, False, False, False)
    """
    This advanced function activates Automatic mode for one day with the settings for Sunday, as set using the Time 
    programmes function. The advanced function is automatically deactivated after 24:00 hours or if you cancel the 
    advanced function first. The heating installation will then return to the pre-set mode.
    """

    QM_PARTY = ('QM_PARTY', True, False, False, False)
    """
    The advanced function brings the room temperature to the set desired Day temperature, in accordance with the set 
    time periods. The advanced function is deactivated after six hours or if you cancel it before the six hours is up. 
    The heating installation will then return to the pre-set mode.
    """

    HOLIDAY = ('HOLIDAY', True, True, True, True)
    """
    """

    @classmethod
    def for_zone(cls) -> list:
        sub_list = []

        for quickMode in QuickMode:
            if quickMode.for_zone:
                sub_list.append(quickMode)

        return sub_list

    @classmethod
    def for_room(cls) -> []:
        sub_list = []

        for quickMode in QuickMode:
            if quickMode.for_room:
                sub_list.append(quickMode)

        return sub_list

    @classmethod
    def for_hot_water(cls) -> []:
        sub_list = []

        for quickMode in QuickMode:
            if quickMode.for_hot_water:
                sub_list.append(quickMode)

        return sub_list

    @classmethod
    def for_circulation(cls) -> []:
        sub_list = []

        for quickMode in QuickMode:
            if quickMode.for_circulation:
                sub_list.append(quickMode)

        return sub_list
