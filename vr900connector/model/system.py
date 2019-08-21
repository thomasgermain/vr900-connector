"""Full system coming from vaillant API."""
import datetime
from typing import List, Optional, Dict

import attr

from . import ActiveMode, HolidayMode, HotWater, Room, Zone, BoilerStatus, \
    Circulation, QuickMode, Error, SystemStatus


@attr.s
class System:
    """This class represents the main class to manipulate vaillant system.
    It is designed to know everything about the system.
    """

    holiday_mode = attr.ib(type=HolidayMode)
    system_status = attr.ib(type=SystemStatus)
    boiler_status = attr.ib(type=Optional[BoilerStatus])
    zones = attr.ib(type=List[Zone])
    rooms = attr.ib(type=List[Room])
    hot_water = attr.ib(type=Optional[HotWater])
    circulation = attr.ib(type=Optional[Circulation])
    outdoor_temperature = attr.ib(type=Optional[float])
    quick_mode = attr.ib(type=Optional[QuickMode])
    errors = attr.ib(type=List[Error])
    _zones = attr.ib(type=Dict[str, Zone], default=dict(), init=False)
    _rooms = attr.ib(type=Dict[str, Room], default=dict(), init=False)

    def __attrs_post_init__(self) -> None:
        """Post init from attrs."""
        if self.holiday_mode is None:
            self.holiday_mode = HolidayMode(False)

        if self.zones:
            self._zones = dict((zone.id, zone) for zone in self.zones)

        if self.rooms:
            self._rooms = dict((room.id, room) for room in self.rooms)

    def set_zone(self, zone_id: str, zone: Zone) -> None:
        """Set *zone* for id."""
        self._zones[zone_id] = zone
        self.zones = list(self._zones.values())

    def set_room(self, room_id: str, room: Room) -> None:
        """Set *room* for id."""
        self._rooms[room_id] = room
        self.rooms = list(self._rooms.values())

    def get_active_mode_zone(self, zone: Zone) -> ActiveMode:
        """Gets current *active mode* for a *room*. This is the only way to get
        it through the vr900connector.
        """
        mode: ActiveMode = zone.active_mode

        # Holiday mode takes precedence over everything
        if self.holiday_mode.active_mode:
            mode = self.holiday_mode.active_mode

        # Global system quick mode takes over zone settings
        if self.quick_mode and self.quick_mode.for_zone:
            if self.quick_mode == QuickMode.QM_VENTILATION_BOOST:
                mode = ActiveMode(Zone.MIN_TEMP, self.quick_mode)

            if self.quick_mode == QuickMode.QM_ONE_DAY_AWAY:
                mode = ActiveMode(zone.target_min_temperature, self.quick_mode)

            if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                mode = ActiveMode(Zone.MIN_TEMP, self.quick_mode)

            if self.quick_mode == QuickMode.QM_ONE_DAY_AT_HOME:
                today = datetime.datetime.now()
                sunday = today - datetime.timedelta(days=today.weekday() - 6)

                time_program = zone.time_program.get_for(sunday)
                mode = ActiveMode(time_program.target_temperature,
                                  self.quick_mode)

            if self.quick_mode == QuickMode.QM_PARTY:
                mode = ActiveMode(zone.target_temperature, self.quick_mode)

        return mode

    def get_active_mode_room(self, room: Room) -> ActiveMode:
        """Gets current *active mode* for a *room*. This is the only way to get
        it through the vr900connector.
        """
        # Holiday mode takes precedence over everything
        if self.holiday_mode.active_mode:
            return self.holiday_mode.active_mode

        # Global system quick mode takes over room settings
        if self.quick_mode and self.quick_mode.for_room:
            if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                return ActiveMode(Room.MIN_TEMP, self.quick_mode)

        return room.active_mode

    def get_active_mode_circulation(self,
                                    circulation: Optional[Circulation] = None)\
            -> Optional[ActiveMode]:
        """Gets current *active mode* for *circulation*. This is the only way
        to get it through the vr900connector.
        """
        if not circulation:
            circulation = self.circulation

        if circulation:
            if self.holiday_mode.active_mode:
                active_mode = self.holiday_mode.active_mode
                active_mode.target_temperature = None
                return active_mode

            if self.quick_mode and self.quick_mode.for_circulation:
                return ActiveMode(None, self.quick_mode)

            return circulation.active_mode
        return None

    def get_active_mode_hot_water(self, hot_water: Optional[HotWater] = None)\
            -> Optional[ActiveMode]:
        """Gets current *active mode* for *hot water*. This is the only way to
        get it through the vr900connector.
        """
        if not hot_water:
            hot_water = self.hot_water

        if hot_water:
            if self.holiday_mode.active_mode:
                active_mode = self.holiday_mode.active_mode
                active_mode.target_temperature = HotWater.MIN_TEMP
                return active_mode

            if self.quick_mode and self.quick_mode.for_hot_water:
                if self.quick_mode == QuickMode.QM_HOTWATER_BOOST:
                    return ActiveMode(hot_water.target_temperature,
                                      self.quick_mode)

                if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                    return ActiveMode(HotWater.MIN_TEMP, self.quick_mode)

                if self.quick_mode == QuickMode.QM_ONE_DAY_AWAY:
                    return ActiveMode(HotWater.MIN_TEMP, self.quick_mode)

            return hot_water.active_mode
        return None
