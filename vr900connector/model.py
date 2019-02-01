from datetime import datetime, date, timedelta
from typing import Dict, List
import copy

from . import constant


class BoilerStatus:
    deviceName: str = None
    code: str = None
    title: str = None
    description: str = None
    hint: str = None
    lastUpdate: datetime = None
    currentTemperature: float = None
    waterPressure: float = None
    waterPressureUnit: str = None


class TimeProgramDaySetting:
    startTime: str = None
    temperature: float = None
    mode: str = None
    absoluteMinutes: int = None

    def __init__(self, start_time: str, temperature: float, mode: str):
        self.startTime = start_time
        self.temperature = temperature
        self.mode = mode
        self.absoluteMinutes = TimeProgramDaySetting.to_absolute_minute(start_time)

    @staticmethod
    def to_absolute_minute(start_time):
        split = start_time.split(":")
        if len(split) > 1:
            hour = int(split[0]) * 60
            minute = int(split[1])
            return hour + minute
        return 0


class TimeProgramDay:
    timeProgramDaySettings: List[TimeProgramDaySetting] = []

    def __init__(self):
        self.timeProgramDaySettings = list()

    def add_setting(self, start_time: str, temperature: float, mode: str):
        self.timeProgramDaySettings.append(TimeProgramDaySetting(start_time, temperature, mode))


class TimeProgram:
    timeProgramDays: Dict[str, TimeProgramDay] = dict()

    def __init__(self):
        self.timeProgramDays = dict()

    def add_day(self, day: str, time_program_day: TimeProgramDay):
        self.timeProgramDays[day] = time_program_day

    def get_setting_for(self, search_date: datetime):
        day = search_date.strftime("%A").lower()
        day_before = (search_date - timedelta(days=1)).strftime("%A").lower()
        time = str(search_date.hour) + ":" + str(search_date.minute)

        absolute_minute = TimeProgramDaySetting.to_absolute_minute(time)
        timeProgramDay = self.timeProgramDays[day]
        timeProgramDayBefore = self.timeProgramDays[day_before]

        """if hour:minute is before the first setting of the day, check the last of day -1"""
        if absolute_minute < timeProgramDay.timeProgramDaySettings[0].absoluteMinutes:
            return timeProgramDayBefore.timeProgramDaySettings[-1]
        else:
            idx = 0
            while idx < len(timeProgramDay.timeProgramDaySettings) - 1:
                if absolute_minute > timeProgramDay.timeProgramDaySettings[idx].absoluteMinutes and \
                        (idx + 1 == len(timeProgramDay.timeProgramDaySettings)
                         or absolute_minute < timeProgramDay.timeProgramDaySettings[idx + 1].absoluteMinutes):
                    return timeProgramDay.timeProgramDaySettings[idx]
                idx += 1

            if idx == 0:
                return timeProgramDay.timeProgramDaySettings[0]
            elif idx == len(timeProgramDay.timeProgramDaySettings) - 1:
                return timeProgramDay.timeProgramDaySettings[-1]
        return None


class BoostMode:
    name: str = None
    forZone: bool = False
    forRoom: bool = False
    forWaterHeater: bool = False
    forCirculation: bool = False

    def __init__(self, name, for_zone, for_room, for_water_heater, for_circulation):
        self.name = name
        self.forZone = for_zone
        self.forRoom = for_room
        self.forWaterHeater = for_water_heater
        self.forCirculation = for_circulation


class BoostModes:
    QM_HOTWATER_BOOST = BoostMode('QM_HOTWATER_BOOST', False, False, True, False)
    QM_VENTILATION_BOOST = BoostMode('QM_VENTILATION_BOOST', True, True, False, False)
    QM_ONE_DAY_AWAY = BoostMode('QM_ONE_DAY_AWAY', True, True, True, False)
    QM_SYSTEM_OFF = BoostMode('QM_SYSTEM_OFF', True, True, True, True)
    QM_ONE_DAY_AT_HOME = BoostMode('QM_ONE_DAY_AT_HOME', True, False, False, False)
    QM_PARTY = BoostMode('QM_PARTY', True, False, False, False)

    _VALUES = {
        QM_HOTWATER_BOOST.name: QM_HOTWATER_BOOST,
        QM_VENTILATION_BOOST.name: QM_VENTILATION_BOOST,
        QM_ONE_DAY_AWAY.name: QM_ONE_DAY_AWAY,
        QM_SYSTEM_OFF.name: QM_SYSTEM_OFF,
        QM_ONE_DAY_AT_HOME.name: QM_ONE_DAY_AT_HOME,
        QM_PARTY.name: QM_PARTY
    }

    @classmethod
    def from_name(cls, name: str):
        return BoostModes._VALUES[name]


class QuickMode:
    boostMode: BoostMode = None
    remainingDuration: int = 0

    def __init__(self, name: str, remaining_duration: int):
        self.boostMode = BoostModes.from_name(name)
        self.remainingDuration = remaining_duration


class QuickVeto:
    remainingTime: int = 0
    targetTemperature: float = None

    def __init__(self, remaining_time, target_temperature):
        self.remainingTime = remaining_time
        self.targetTemperature = target_temperature


class HolidayMode:
    active: bool = False
    startDate: date = None
    endDate: date = None
    targetTemperature: float = None


class ActiveMode:
    targetTemperature: float = None
    name: str = None
    sub_mode: str = None

    def __init__(self, target_temperature: float, name: str, sub_mode: str = None):
        self.targetTemperature = target_temperature
        self.name = name
        self.sub_mode = sub_mode


class Component:
    id: str = None
    name: str = None
    timeProgram: TimeProgram = None
    currentTemperature: float = None
    targetTemperature: float = None
    operationMode: str = None
    quickVeto: QuickVeto = None

    def get_current_time_program(self):
        if self.quickVeto:
            return TimeProgramDaySetting(str(self.quickVeto.remainingTime),
                                         self.quickVeto.targetTemperature, constant.THERMOSTAT_QUICK_VETO)

        return self.timeProgram.get_setting_for(datetime.now())


class Device:
    name: str = None
    sgtin: str = None
    deviceType: str
    isBatteryLow: bool = False
    isRadioOutOfReach: bool = False


class Room(Component):
    childLock: bool = False
    isWindowOpen: bool = False
    devices: List[Device] = []

    def get_current_time_program(self):
        mode = copy.deepcopy(super().get_current_time_program())
        if self.quickVeto is None:
            if self.operationMode == constant.THERMOSTAT_ROOM_MODE_OFF:
                mode = TimeProgramDaySetting(str(0), constant.THERMOSTAT_MIN_TEMP, constant.THERMOSTAT_ROOM_MODE_OFF)
            elif mode.mode == constant.THERMOSTAT_ROOM_MODE_MANUAL:
                mode.temperature = self.targetTemperature
            else:
                if mode.temperature >= self.targetTemperature:
                    mode.mode = constant.THERMOSTAT_ROOM_MODE_AUTO_OFF
                else:
                    mode.mode = constant.THERMOSTAT_ROOM_MODE_AUTO_ON
        return mode


class Zone(Component):
    targetMinTemperature: float = None
    activeFunction: str = None
    rooms: List[Room] = []
    rbr: bool = False

    def get_current_time_program(self):
        mode = copy.deepcopy(super().get_current_time_program())
        if self.quickVeto is None:
            if self.operationMode == constant.THERMOSTAT_ZONE_MODE_OFF:
                mode = TimeProgramDaySetting(str(0), constant.THERMOSTAT_MIN_TEMP, constant.THERMOSTAT_ZONE_MODE_OFF)
            elif mode.mode == constant.THERMOSTAT_ROOM_MODE_MANUAL:
                mode.temperature = self.targetTemperature
            elif mode.mode == constant.THERMOSTAT_ZONE_MODE_DAY:
                mode.temperature = self.targetTemperature
            else:
                mode.temperature = self.targetMinTemperature
        return mode


class DomesticHotWater(Component):

    def get_current_time_program(self):
        """There is no quick veto for hot water"""
        if self.operationMode == constant.HOT_WATER_MODE_ON:
            return TimeProgramDaySetting(str(0), self.targetTemperature, constant.HOT_WATER_MODE_ON)
        elif self.operationMode == constant.HOT_WATER_MODE_OFF:
            return TimeProgramDaySetting(str(0), constant.HOT_WATER_MIN_TEMP, constant.HOT_WATER_MODE_OFF)
        elif self.operationMode == constant.HOT_WATER_MODE_BOOST:
            return TimeProgramDaySetting(str(0), self.targetTemperature, constant.HOT_WATER_MODE_BOOST)
        else:
            # Mode AUTO
            mode = copy.deepcopy(super().get_current_time_program())
            if mode.mode == constant.HOT_WATER_MODE_ON:
                mode.mode = constant.HOT_WATER_MODE_AUTO_ON
                mode.temperature = self.targetTemperature
            else:
                mode.mode = constant.HOT_WATER_MODE_AUTO_OFF
                mode.temperature = constant.HOT_WATER_MIN_TEMP
            return mode


class Circulation(Component):

    def get_current_time_program(self):
        """There is no quick veto for circulation"""
        mode = copy.deepcopy(super().get_current_time_program())
        if mode.mode == constant.CIRCULATION_MODE_ON:
            mode.mode = constant.CIRCULATION_MODE_AUTO_ON
        else:
            mode.mode = constant.CIRCULATION_MODE_AUTO_OFF
        return mode


class VaillantSystem:
    _holidayMode: HolidayMode = HolidayMode()
    _boilerStatus: BoilerStatus = None
    _zones: Dict[str, Zone] = dict()
    _rooms: Dict[str, Room] = dict()
    _hotWater: DomesticHotWater = None
    _circulation: Circulation = None
    _outdoorTemperature: float = None
    _quickMode: QuickMode = None

    def __init__(self, holiday_mode, boiler_status, zones, hot_water, circulation, outdoor_temp, quick_mode):
        if holiday_mode:
            self._holidayMode = holiday_mode
        self._boilerStatus = boiler_status

        if zones:
            self._zones = dict((zone.id, zone) for zone in zones)
            for zone in zones:
                if zone.rbr:
                    for room in zone.rooms:
                        room.zone = zone
                        self._rooms[room.id] = room

        self._hotWater = hot_water
        self._circulation = circulation
        self._outdoorTemperature = outdoor_temp
        self._quickMode = quick_mode
        
    def get_rooms(self):
        return self._rooms.values()

    def get_zones(self):
        return self._zones.values()
            
    def get_active_mode(self, component_id: str):
        zone = self._zones[component_id]
        if zone:
            return self._get_active_mode_zone(zone)

        room = self._rooms[component_id]
        if room:
            return self._get_active_mode_room(room)

        if self._hotWater.id == component_id:
            return self._get_active_mode_hot_water(self._hotWater)

        if self._circulation.id == component_id:
            return self._get_active_mode_circulation(self._circulation)

        return None

    def get_active_mode_zone(self, zone: Zone):
        """Holiday mode takes precedence over everything"""
        if self._holidayMode.active:
            return ActiveMode(self._holidayMode.targetTemperature, constant.HOLIDAY_MODE)

        """Global system quick mode takes over zone settings"""
        if self._quickMode and self._quickMode.boostMode.forZone:
            if self._quickMode.boostMode == BoostModes.QM_VENTILATION_BOOST:
                return ActiveMode(constant.THERMOSTAT_MIN_TEMP, self._quickMode.boostMode.name)

            if self._quickMode.boostMode == BoostModes.QM_ONE_DAY_AWAY:
                return ActiveMode(zone.targetMinTemperature, self._quickMode.boostMode.name)

            if self._quickMode.boostMode == BoostModes.QM_SYSTEM_OFF:
                return ActiveMode(constant.THERMOSTAT_MIN_TEMP, self._quickMode.boostMode.name)

            if self._quickMode.boostMode == BoostModes.QM_ONE_DAY_AT_HOME:
                return ActiveMode(zone.targetTemperature, self._quickMode.boostMode.name)

            if self._quickMode.boostMode == BoostModes.QM_PARTY:
                return ActiveMode(zone.targetTemperature, self._quickMode.boostMode.name)

            return None

        time_program = zone.get_current_time_program()
        return ActiveMode(time_program.temperature, zone.operationMode, time_program.mode)

    def get_active_mode_room(self, room: Room):
        """Holiday mode takes precedence over everything"""
        if self._holidayMode.active:
            return ActiveMode(self._holidayMode.targetTemperature, constant.HOLIDAY_MODE)

        """Global system quick mode takes over zone settings"""
        if self._quickMode and self._quickMode.boostMode.forRoom:
            if self._quickMode.boostMode == BoostModes.QM_VENTILATION_BOOST:
                return ActiveMode(constant.THERMOSTAT_MIN_TEMP, self._quickMode.boostMode.name)

            if self._quickMode.boostMode == BoostModes.QM_ONE_DAY_AWAY:
                return ActiveMode(room.zone.targetMinTemperature, self._quickMode.boostMode.name)

            if self._quickMode.boostMode == BoostModes.QM_SYSTEM_OFF:
                return ActiveMode(constant.THERMOSTAT_MIN_TEMP, self._quickMode.boostMode.name)

            return None

        time_program = room.get_current_time_program()
        return ActiveMode(time_program.temperature, room.operationMode, time_program.mode)

    def get_active_mode_circulation(self, circulation: Circulation = None):
        if not circulation:
            circulation = self._circulation

        if self._holidayMode.active:
            return ActiveMode(0, constant.HOLIDAY_MODE)

        if self._quickMode and self._quickMode.boostMode.forCirculation:
            if self._quickMode.boostMode == BoostModes.QM_SYSTEM_OFF:
                return ActiveMode(0, self._quickMode.boostMode.name)

        time_program = circulation.get_current_time_program()
        return ActiveMode(0, circulation.operationMode, time_program.mode)

    def get_active_mode_hot_water(self, hot_water: DomesticHotWater = None):
        if not hot_water:
            hot_water = self._hotWater

        if self._holidayMode.active:
            return ActiveMode(self._holidayMode.targetTemperature, constant.HOLIDAY_MODE)

        if self._quickMode and self._quickMode.boostMode.forWaterHeater:
            if self._quickMode.boostMode == BoostModes.QM_HOTWATER_BOOST:
                return ActiveMode(hot_water.targetTemperature, self._quickMode.boostMode.name)

        time_program = hot_water.get_current_time_program()
        return ActiveMode(time_program.temperature, hot_water.operationMode, time_program.mode)
