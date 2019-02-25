import datetime
from typing import List

from . import ActiveMode, HolidayMode, HotWater, Room, Zone, BoilerStatus, Circulation, QuickMode, HeatingMode


class System:
    """
    This class represents the main class to manipulate vaillant system. This class is designed to know everything (or
    at least to know to who it has to delegate to know) about the system.

    If your are using :class:`vr900connector.SystemManager`, you should only use this class to interact with the system

    Args:
        holiday_mode: See :class:`vr900connector.HolidayMode`
        boiler_status: See :class:`vr900connector.BoilerStatus`
        zones: List of :class:`vr900connector.Zone` available in the system
        rooms: List of :class:`vr900connector.Room` available in the system
        hot_water: See :class:`vr900connector.HotWater`
        circulation: See :class:`vr900connector.Circulation`
        outdoor_temperature: Outdoor temperature, if available
        quick_mode: A :class:`vr900connector.QuickMode` if any is running on
    """

    def __init__(self, holiday_mode: HolidayMode, boiler_status: BoilerStatus, zones: List[Zone], rooms: List[Room],
                 hot_water: HotWater, circulation: Circulation, outdoor_temperature: float, quick_mode: QuickMode):
        if holiday_mode:
            self.holiday_mode = holiday_mode
        else:
            self.holiday_mode = HolidayMode(False, None, None, None)

        self.boiler_status = boiler_status

        if zones:
            self.zones = zones
            self._zones_dict = dict((zone.id, zone) for zone in zones)
        else:
            self._zones_dict = dict()
            self.zones = []

        if rooms:
            self.rooms = rooms
            self._rooms_dict = dict((room.id, room) for room in rooms)
        else:
            self._rooms_dict = dict()
            self.rooms = []

        self.hot_water = hot_water
        self.circulation = circulation
        self.outdoor_temperature = outdoor_temperature
        self.quick_mode = quick_mode

    def get_zone(self, zone_id: str) -> Zone:
        return self._zones_dict[zone_id]

    def get_room(self, room_id: int) -> Room:
        return self._rooms_dict[int(room_id)]

    def get_active_mode_zone(self, zone: Zone) -> ActiveMode:
        # Holiday mode takes precedence over everything
        if self.holiday_mode.active:
            return self.holiday_mode.active_mode

        # Global system quick mode takes over zone settings
        if self.quick_mode and self.quick_mode.for_zone:
            if self.quick_mode == QuickMode.QM_VENTILATION_BOOST:
                return ActiveMode(Zone.MIN_TEMP, self.quick_mode)

            if self.quick_mode == QuickMode.QM_ONE_DAY_AWAY:
                return ActiveMode(zone.target_min_temperature, self.quick_mode)

            if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                return ActiveMode(Zone.MIN_TEMP, self.quick_mode)

            if self.quick_mode == QuickMode.QM_ONE_DAY_AT_HOME:
                today = datetime.datetime.now()
                sunday = today - datetime.timedelta(days=today.weekday() - 6)

                time_program = zone.time_program.get_time_program_for(sunday)
                return ActiveMode(time_program.target_temperature, self.quick_mode)

            if self.quick_mode == QuickMode.QM_PARTY:
                return ActiveMode(zone.target_temperature, self.quick_mode)

        return zone.active_mode

    def get_active_mode_room(self, room: Room) -> ActiveMode:
        # Holiday mode takes precedence over everything
        if self.holiday_mode.active:
            return self.holiday_mode.active_mode

        # Global system quick mode takes over room settings
        if self.quick_mode and self.quick_mode.for_room:
            if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                return ActiveMode(Room.MIN_TEMP, self.quick_mode)

        return room.active_mode

    def get_active_mode_circulation(self, circulation: Circulation = None) -> ActiveMode:
        if not circulation:
            circulation = self.circulation

        if self.holiday_mode.active:
            active_mode = self.holiday_mode.active_mode
            active_mode.target_temperature = None
            return active_mode

        if self.quick_mode and self.quick_mode.for_circulation:
            if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                return ActiveMode(None, self.quick_mode)

            if self.quick_mode == QuickMode.QM_HOTWATER_BOOST:
                return ActiveMode(None, self.quick_mode)

        return circulation.active_mode

    def get_active_mode_hot_water(self, hot_water: HotWater = None) -> ActiveMode:
        if not hot_water:
            hot_water = self.hot_water

        if self.holiday_mode.active:
            active_mode = self.holiday_mode.active_mode
            active_mode.target_temperature = HotWater.MIN_TEMP
            return active_mode

        if self.quick_mode and self.quick_mode.for_hot_water:
            if self.quick_mode == QuickMode.QM_HOTWATER_BOOST:
                return ActiveMode(hot_water.target_temperature, self.quick_mode)

            if self.quick_mode == QuickMode.QM_SYSTEM_OFF:
                return ActiveMode(HotWater.MIN_TEMP, self.quick_mode)

        return hot_water.active_mode
