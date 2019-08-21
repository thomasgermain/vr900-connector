"""Components of vaillant system"""
import abc
from typing import Optional, List
from datetime import datetime
import attr

from . import Mode, TimeProgram, QuickVeto, ActiveMode, OperationMode, \
    constants


# pylint: disable=too-few-public-methods
@attr.s
class Component:
    """This is a common class for a component in the system.
    A component can be *Room*, *Zone*, *HotWater*, *Circulation*.

    It allows you to get the *ActiveMode*.
    """

    id = attr.ib(type=str)
    name = attr.ib(type=Optional[str])
    time_program = attr.ib(type=TimeProgram)
    current_temperature = attr.ib(type=Optional[float])
    target_temperature = attr.ib(type=Optional[float])
    operation_mode = attr.ib(type=OperationMode)
    quick_veto = attr.ib(type=Optional[QuickVeto])

    @property
    def active_mode(self) -> ActiveMode:
        """Gets the  active mode for a component.

        **Please note that a component is not aware of quick mode or
        holiday mode.**
        """

        if self.quick_veto:
            return ActiveMode(self.quick_veto.target_temperature,
                              OperationMode.QUICK_VETO)

        if self.operation_mode == OperationMode.AUTO:
            setting = self.time_program.get_for(datetime.now())
            if setting.target_temperature:
                return ActiveMode(setting.target_temperature,
                                  OperationMode.AUTO, setting.mode)

        return self._get_specific_active_mode()

    @abc.abstractmethod
    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""


# pylint: disable=too-few-public-methods
@attr.s
class Circulation(Component):
    """This is representing the circulation from the system.
    This is quite a special component since there is no
    *current_temperature*, *target_temperature* nor *quick_veto*.
    """

    MODES: List[Mode] = [OperationMode.ON, OperationMode.OFF,
                         OperationMode.AUTO]

    current_temperature = attr.ib(default=None, init=False)
    target_temperature = attr.ib(default=None, init=False)
    quick_veto = attr.ib(default=None, init=False)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operation_mode == OperationMode.AUTO:
            setting = self.time_program.get_for(datetime.now())
            mode = ActiveMode(None, OperationMode.AUTO, setting.mode)
        else:
            mode = ActiveMode(None, self.operation_mode)
        return mode


# pylint: disable=too-few-public-methods
@attr.s
class HotWater(Component):
    """This is representing the hot water from the system.

    There is no *quick_veto* available for this component.
    """

    MODES = [OperationMode.ON, OperationMode.OFF, OperationMode.AUTO]
    MIN_TEMP = 35
    MAX_TEMP = 70

    quick_veto = attr.ib(default=None, init=False)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operation_mode == OperationMode.AUTO:
            setting = self.time_program.get_for(datetime.now())

            if setting.mode == OperationMode.ON:
                mode = ActiveMode(self.target_temperature, OperationMode.AUTO,
                                  setting.mode)
            else:
                mode = ActiveMode(HotWater.MIN_TEMP, OperationMode.AUTO,
                                  setting.mode)

        elif self.operation_mode == OperationMode.ON:
            mode = ActiveMode(self.target_temperature, OperationMode.ON)
        else:  # MODE_OFF
            mode = ActiveMode(HotWater.MIN_TEMP, OperationMode.OFF)

        return mode


# pylint: disable=too-few-public-methods
@attr.s
class Device:
    """ A device is a physical component of a *room*. It can be a VR50 or a
    VR51.
    """

    name = attr.ib(type=str)
    sgtin = attr.ib(type=str)
    device_type = attr.ib(type=str)
    battery_low = attr.ib(type=bool)
    radio_out_of_reach = attr.ib(type=bool)


# pylint: disable=too-few-public-methods
@attr.s
class Room(Component):
    """This is representing a *room* from the system."""

    MODES = [OperationMode.OFF, OperationMode.MANUAL, OperationMode.AUTO,
             OperationMode.QUICK_VETO]
    MIN_TEMP = constants.FROST_PROTECTION_TEMP
    MAX_TEMP = constants.THERMOSTAT_MAX_TEMP

    child_lock = attr.ib(type=bool)
    window_open = attr.ib(type=bool)
    devices = attr.ib(type=List[Device])
    humidity = attr.ib(type=Optional[float], default=None)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operation_mode == OperationMode.OFF:
            mode = ActiveMode(self.MIN_TEMP, OperationMode.OFF)
        else:  # MODE_MANUAL
            mode = ActiveMode(self.target_temperature, OperationMode.MANUAL)

        return mode

# pylint: disable=too-few-public-methods
@attr.s
class Zone(Component):
    """This is representing a *zone* from the system

    If *rbr* (Room By Room) is True, the zone itself doesn't mean anything
    anymore, it means rooms are 'controlling' the zone.
    """

    MODES = [OperationMode.AUTO, OperationMode.OFF, OperationMode.DAY,
             OperationMode.NIGHT, OperationMode.QUICK_VETO]
    MIN_TEMP = constants.FROST_PROTECTION_TEMP
    MAX_TEMP = constants.THERMOSTAT_MAX_TEMP

    target_min_temperature = attr.ib(type=float)
    active_function = attr.ib(type=str)
    rbr = attr.ib(type=bool)

    def _get_specific_active_mode(self) -> ActiveMode:
        """Gets specific active mode for a component."""
        if self.operation_mode == OperationMode.AUTO:
            setting = self.time_program.get_for(datetime.now())

            if setting.mode == OperationMode.DAY:
                mode = ActiveMode(self.target_temperature, OperationMode.AUTO,
                                  setting.mode)
            else:
                mode = ActiveMode(self.target_min_temperature,
                                  OperationMode.AUTO, setting.mode)
        elif self.operation_mode == OperationMode.OFF:
            mode = ActiveMode(self.MIN_TEMP, OperationMode.OFF)
        elif self.operation_mode == OperationMode.DAY:
            mode = ActiveMode(self.target_temperature, OperationMode.DAY)
        else:  # MODE_NIGHT
            mode = ActiveMode(self.target_min_temperature, OperationMode.NIGHT)

        return mode
