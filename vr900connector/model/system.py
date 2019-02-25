import datetime

from . import ActiveMode, HolidayMode, constants,  HotWater, Room, Zone
from .quickmode import SYSTEM_OFF, HOTWATER_BOOST, PARTY, ONE_DAY_AT_HOME, ONE_DAY_AWAY, VENTILATION_BOOST


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

    def __init__(self, holiday_mode, boiler_status, zones, rooms, hot_water, circulation, outdoor_temperature, quick_mode):
        if holiday_mode:
            self.holiday_mode = holiday_mode
        else:
            self.holiday_mode = HolidayMode(False, None, None, None)

        self.boiler_status = boiler_status

        if zones:
            self.zones = zones
            self.rooms = rooms
            self._zones_dict = dict((zone.id, zone) for zone in zones)
            self._rooms_dict = dict((room.id, room) for room in rooms)
        else:
            self._zones_dict = dict()
            self._rooms_dict = dict()

        self.hot_water = hot_water
        self.circulation = circulation
        self.outdoor_temperature = outdoor_temperature
        self.quick_mode = quick_mode

    def get_zone(self, zone_id):
        return self._zones_dict[str(zone_id)]

    def get_room(self, room_id):
        return self._rooms_dict[int(room_id)]

    def get_active_mode_zone(self, zone):
        # Holiday mode takes precedence over everything
        if self.holiday_mode.active:
            return ActiveMode(self.holiday_mode.target_temperature, constants.HOLIDAY_MODE)

        # Global system quick mode takes over zone settings
        if self.quick_mode and self.quick_mode.for_zone:
            if self.quick_mode == VENTILATION_BOOST:
                return ActiveMode(Zone.MIN_TEMP, self.quick_mode.name)

            if self.quick_mode == ONE_DAY_AWAY:
                return ActiveMode(zone.target_min_temperature, self.quick_mode.name)

            if self.quick_mode == SYSTEM_OFF:
                return ActiveMode(Zone.MIN_TEMP, self.quick_mode.name)

            if self.quick_mode == ONE_DAY_AT_HOME:
                today = datetime.datetime.now()
                sunday = today - datetime.timedelta(days=today.weekday() - 6)

                time_program = zone.time_program.get_time_program_for(sunday)
                return ActiveMode(time_program.target_temperature, time_program.mode)

            if self.quick_mode == PARTY:
                return ActiveMode(zone.target_temperature, self.quick_mode.name)

            return None

        time_program = zone.get_current_time_program()
        return ActiveMode(time_program.target_temperature, time_program.mode)

    def get_active_mode_room(self, room):
        # Holiday mode takes precedence over everything
        if self.holiday_mode.active:
            return ActiveMode(self.holiday_mode.target_temperature, constants.HOLIDAY_MODE)

        # Global system quick mode takes over room settings
        if self.quick_mode and self.quick_mode.for_room:
            if self.quick_mode == VENTILATION_BOOST:
                return ActiveMode(Room.MIN_TEMP, self.quick_mode.name)

            # if self.quick_mode == ONE_DAY_AWAY:
                # Regarding the documentation, the quick mode should override time program, but it doesn't,
                # I personally tested it

            if self.quick_mode == SYSTEM_OFF:
                return ActiveMode(Room.MIN_TEMP, self.quick_mode.name)

        time_program = room.get_current_time_program()
        return ActiveMode(time_program.target_temperature, time_program.mode)

    def get_active_mode_circulation(self, circulation=None):
        if not circulation:
            circulation = self.circulation

        if self.holiday_mode.active:
            return ActiveMode(0, constants.HOLIDAY_MODE)

        if self.quick_mode and self.quick_mode.for_circulation:
            if self.quick_mode == SYSTEM_OFF:
                return ActiveMode(0, self.quick_mode.name)

        time_program = circulation.get_current_time_program()
        return ActiveMode(time_program.target_temperature, time_program.mode)

    def get_active_mode_hot_water(self, hot_water=None):
        if not hot_water:
            hot_water = self.hot_water

        if self.holiday_mode.active:
            return ActiveMode(self.holiday_mode.target_temperature, constants.HOLIDAY_MODE)

        if self.quick_mode and self.quick_mode.for_hot_water:
            if self.quick_mode == HOTWATER_BOOST:
                return ActiveMode(hot_water.target_temperature, self.quick_mode.name)

            if self.quick_mode == SYSTEM_OFF:
                return ActiveMode(HotWater.MIN_TEMP, self.quick_mode.name)

        time_program = hot_water.get_current_time_program()
        return ActiveMode(time_program.target_temperature, time_program.mode)
