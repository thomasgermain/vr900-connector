"""Vaillant operation modes."""
from enum import Enum
from datetime import date
from typing import Optional, List
import attr


# pylint: disable=too-few-public-methods
class Mode:
    """Base class for mode."""


# pylint: disable=too-few-public-methods
class QuickVeto(Mode):
    """Represents a quick veto which can be applied to a zone or a room.

    For a room, quick veto duration is customizable and it's possible to
    get the remaining duration through the API.

    For a zone, quick veto duration is NOT customizable (6 hours) and the API
    returns always *0* as remaining duration.
    """

    def __init__(self, remaining_time: int, target_temperature: float) -> None:
        if remaining_time > 1440:
            raise ValueError(remaining_time)
        self.remaining_time = remaining_time
        self.target_temperature = target_temperature


class OperationMode(Mode, Enum):
    """Represents all the heating mode available in the API."""

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
    """This class is a helper to check what is impacted by a quick mode.

    Quick modes are mode you can quickly set with the mobile app.

    Most of the times, quick modes have system wise impact.

    This is different from quick veto, which will only impact one component.

    Quick mode are taking precedence in case of simultaneous quick veto
    and quick mode.

    Note that there is a default duration for quick modes(which can't be
    changed) but the API always returns *0* as remaining duration, so there is
    no way to know when quick mode will end.

    Vaillant documentation link:
    http://elearning.vaillant.com/vrc700/ci/en/documents/uk/infopool/Operating_instructions.pdf
    """

    # pylint: disable=too-many-arguments
    def __init__(self, mode_name: str, for_zone: bool, for_room: bool,
                 for_hot_water: bool, for_circulation: bool):
        self._mode_name = mode_name
        self.for_zone = for_zone
        self.for_room = for_room
        self.for_hot_water = for_hot_water
        self.for_circulation = for_circulation

    QM_HOTWATER_BOOST = ('QM_HOTWATER_BOOST', False, False, True, True)
    """The advanced function heats the water in the domestic hot water cylinder
    once until the desired DHW circuit temperature set is reached or until you
    cancel the advanced function early.
    The heating installation will then return to the pre-set mode
    """

    QM_VENTILATION_BOOST = ('QM_VENTILATION_BOOST', True, False, False, False)
    """This advanced function switches the zone off for 30 minutes.
    The frost protection function is activated, and hot water generation and
    circulation remain active.
    Ventilation is activated and works at the highest ventilation level.
    The advanced function is automatically deactivated after 30 minutes or
    if you cancel the advanced function early.
    The heating installation will then return to the pre-set mode.
    """

    QM_ONE_DAY_AWAY = ('QM_ONE_DAY_AWAY', True, False, True, True)
    """Hot water generation and circulation are switched off and the frost
    protection is activated.
    The advanced function is automatically deactivated after 24:00 hours or if
    you cancel the advanced function first.
    The heating installation will then return to the pre-set mode.
    Ventilation is activated and works at the lowest ventilation level.
    """

    QM_SYSTEM_OFF = ('QM_SYSTEM_OFF', True, True, True, True)
    """The heating function, hot water circuit and cooling are switched off.
    The frost protection function is activated.
    The circulation is switched off.
    Ventilation is activated and works at the lowest ventilation level.
    """

    QM_ONE_DAY_AT_HOME = ('QM_ONE_DAY_AT_HOME', True, False, False, False)
    """This advanced function activates Automatic mode for one day with the
    settings for Sunday, as set using the Time programmes function.
    The advanced function is automatically deactivated after 24:00 hours or if
    you cancel the advanced function first.
    The heating installation will then return to the pre-set mode.
    """

    QM_PARTY = ('QM_PARTY', True, False, False, False)
    """The advanced function brings the room temperature to the set desired
    Day temperature, in accordance with the set time periods.
    The advanced function is deactivated after six hours or if you cancel it
    before the six hours is up.
    The heating installation will then return to the pre-set mode.
    """

    QM_HOLIDAY = ('QM_HOLIDAY', True, True, True, True)
    """
    """

    QM_QUICK_VETO = ('QM_QUICK_VETO', False, False, False, False)
    """
    This advanced function activates a quick veto for one specific zone
    """

    @classmethod
    def get_for_zone(cls) -> List['QuickMode']:
        """Gets the list of quick modes application to zones."""
        sub_list = []

        for quick_mode in QuickMode:
            if quick_mode.for_zone:
                sub_list.append(quick_mode)

        return sub_list

    @classmethod
    def get_for_room(cls) -> List['QuickMode']:
        """Gets the list of quick modes application to rooms."""
        sub_list = []

        for quick_mode in QuickMode:
            if quick_mode.for_room:
                sub_list.append(quick_mode)

        return sub_list

    @classmethod
    def get_for_hot_water(cls) -> List['QuickMode']:
        """Gets the list of quick modes application to hot water."""
        sub_list = []

        for quick_mode in QuickMode:
            if quick_mode.for_hot_water:
                sub_list.append(quick_mode)

        return sub_list

    @classmethod
    def get_for_circulation(cls) -> List['QuickMode']:
        """Gets the list of quick modes application to circulation."""
        sub_list = []

        for quick_mode in QuickMode:
            if quick_mode.for_circulation:
                sub_list.append(quick_mode)

        return sub_list


@attr.s
class ActiveMode:
    """Active mode represent to current active mode for a component.

    Since it can be quite complex to get the real active mode, actually,
    the API returns pieces at different places like for example:
    - the configured mode for a room/zone/hot water/circulation
    - the quick mode (if any)

    But, if a zone is configured in 'AUTO' mode and there is a quick mode
    *System off* active, the API will still return *AUTO* for the zone's
    operation mode, while quick mode will actually take precedence. And of
    course, *System off* quick mode will have some impact on target
    temperature.

    So the active mode will let you know the real active mode and the target
    temperature. When *current_mode* is *AUTO* you will also be able to know
    the *sub_mode* (*ON*/*OFF*) except for a room.

    Please not there is not *target_temperature* for *circulation* component.
    """

    target_temperature = attr.ib(type=Optional[float])
    current_mode = attr.ib(type=Mode)
    sub_mode = attr.ib(type=Optional[Mode], default=None)


@attr.s
class HolidayMode:
    """Represents system's holiday mode.

    *active* means the user has activated the holiday mode.

    *is_currently_active* means it's *active* and today is between *start_date*
    and *end_date*.
    """

    active = attr.ib(type=bool)
    start_date = attr.ib(type=Optional[date], default=None)
    end_date = attr.ib(type=Optional[date], default=None)
    target_temperature = attr.ib(type=Optional[float], default=None)

    @property
    def active_mode(self) -> Optional[ActiveMode]:
        """Get active mode from holiday mode if active."""
        if self.is_currently_active:
            return ActiveMode(self.target_temperature, QuickMode.QM_HOLIDAY)
        return None

    @property
    def is_currently_active(self) -> bool:
        """if holiday is active and today is between start and end date."""
        return self.active \
            and self.start_date is not None \
            and self.end_date is not None \
            and self.start_date <= date.today() <= self.end_date
