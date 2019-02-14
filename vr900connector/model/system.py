from . import constant, ActiveMode, HolidayMode
from .boostmode import QM_SYSTEM_OFF, QM_HOTWATER_BOOST, QM_PARTY, QM_ONE_DAY_AT_HOME, QM_ONE_DAY_AWAY, \
    QM_VENTILATION_BOOST


class System:
    holidayMode = HolidayMode()
    boilerStatus = None
    _zones = dict()
    _rooms = dict()
    hotWater = None
    circulation = None
    outdoorTemperature = None
    quickMode = None

    def __init__(self, holiday_mode, boiler_status, zones, hot_water, circulation, outdoor_temp, quick_mode):
        if holiday_mode:
            self.holidayMode = holiday_mode
        self.boilerStatus = boiler_status

        if zones:
            self._zones = dict((zone.id, zone) for zone in zones)
            for zone in zones:
                if zone.rbr:
                    for room in zone.rooms:
                        room.zone = zone
                        self._rooms[room.id] = room

        self.hotWater = hot_water
        self.circulation = circulation
        self.outdoorTemperature = outdoor_temp
        self.quickMode = quick_mode

    def get_rooms(self):
        return self._rooms.values()

    def get_zones(self):
        return self._zones.values()

    def get_zone(self, zone_id):
        return self._zones[str(zone_id)]

    def get_room(self, room_id):
        return self._rooms[int(room_id)]

    def get_active_mode_zone(self, zone):
        """Holiday mode takes precedence over everything"""
        if self.holidayMode.active:
            return ActiveMode(self.holidayMode.targetTemperature, constant.HOLIDAY_MODE)

        """Global system quick mode takes over zone settings"""
        if self.quickMode and self.quickMode.boostMode.forZone:
            if self.quickMode.boostMode == QM_VENTILATION_BOOST:
                return ActiveMode(constant.FROST_PROTECTION_TEMP, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_ONE_DAY_AWAY:
                return ActiveMode(zone.targetMinTemperature, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_SYSTEM_OFF:
                return ActiveMode(constant.FROST_PROTECTION_TEMP, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_ONE_DAY_AT_HOME:
                return ActiveMode(zone.targetTemperature, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_PARTY:
                return ActiveMode(zone.targetTemperature, self.quickMode.boostMode.name)

            return None

        time_program = zone.get_current_time_program()
        if zone.quickVeto:
            return ActiveMode(time_program.temperature, time_program.mode)

        return ActiveMode(time_program.temperature, zone.operationMode, time_program.mode)

    def get_active_mode_room(self, room):
        """Holiday mode takes precedence over everything"""
        if self.holidayMode.active:
            return ActiveMode(self.holidayMode.targetTemperature, constant.HOLIDAY_MODE)

        """Global system quick mode takes over zone settings"""
        if self.quickMode and self.quickMode.boostMode.forRoom:
            if self.quickMode.boostMode == QM_VENTILATION_BOOST:
                return ActiveMode(constant.FROST_PROTECTION_TEMP, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_ONE_DAY_AWAY:
                return ActiveMode(room.zone.targetMinTemperature, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_SYSTEM_OFF:
                return ActiveMode(constant.FROST_PROTECTION_TEMP, self.quickMode.boostMode.name)

            return None

        time_program = room.get_current_time_program()
        if room.quickVeto:
            return ActiveMode(time_program.temperature, time_program.mode)

        return ActiveMode(time_program.temperature, room.operationMode, time_program.mode)

    def get_active_mode_circulation(self, circulation=None):
        if not circulation:
            circulation = self.circulation

        if self.holidayMode.active:
            return ActiveMode(0, constant.HOLIDAY_MODE)

        if self.quickMode and self.quickMode.boostMode.forCirculation:
            if self.quickMode.boostMode == QM_SYSTEM_OFF:
                return ActiveMode(0, self.quickMode.boostMode.name)

        time_program = circulation.get_current_time_program()
        return ActiveMode(0, circulation.operationMode, time_program.mode)

    def get_active_mode_hot_water(self, hot_water=None):
        if not hot_water:
            hot_water = self.hotWater

        if self.holidayMode.active:
            return ActiveMode(self.holidayMode.targetTemperature, constant.HOLIDAY_MODE)

        if self.quickMode and self.quickMode.boostMode.forWaterHeater:
            if self.quickMode.boostMode == QM_HOTWATER_BOOST:
                return ActiveMode(hot_water.targetTemperature, self.quickMode.boostMode.name)

            if self.quickMode.boostMode == QM_SYSTEM_OFF:
                return ActiveMode(constant.FROST_PROTECTION_TEMP, self.quickMode.boostMode.name)

        time_program = hot_water.get_current_time_program()
        return ActiveMode(time_program.temperature, hot_water.operationMode, time_program.mode)
