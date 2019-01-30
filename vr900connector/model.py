from datetime import datetime, date, timedelta
from typing import Dict, List
import copy
from . import constant


class BoilerStatus:
    deviceName: str
    code: str
    title: str
    description: str
    hint: str
    lastUpdate: datetime
    currentTemperature: float
    waterPressure: float
    waterPressureUnit: str


class TimeProgramDaySetting:
    startTime: str
    temperature: float
    mode: str
    absoluteMinutes: int

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
    timeProgramDaySettings: List[TimeProgramDaySetting]

    def __init__(self):
        self.timeProgramDaySettings = list()

    def add_setting(self, start_time: str, temperature: float, mode: str):
        self.timeProgramDaySettings.append(TimeProgramDaySetting(start_time, temperature, mode))


class TimeProgram:
    timeProgramDays: Dict[str, TimeProgramDay]

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


class QuickMode:
    name: str
    remainingDuration: int

    def __init__(self, name: str, remaining_duration: int):
        self.name = name
        self.remainingDuration = remaining_duration


class QuickVeto:
    remainingTime: int
    configuredTemperature: float

    def __init__(self, remaining_time, configured_temperature):
        self.remainingTime = remaining_time
        self.configuredTemperature = configured_temperature


class Heated:
    id: str
    name: str
    timeProgram: TimeProgram
    currentTemperature: float
    targetTemperature: float
    operationMode: str
    quickVeto: QuickVeto = None
    availableOperationModes: List[str]

    def get_active_mode(self):
        if self.quickVeto:
            return TimeProgramDaySetting(str(self.quickVeto.remainingTime),
                                         self.quickVeto.configuredTemperature, "QUICK_VETO")

        return self.timeProgram.get_setting_for(datetime.now())


class Device:
    name: str
    sgtin: str
    deviceType: str
    isBatteryLow: bool
    isRadioOutOfReach: bool


class Room(Heated):
    childLock: bool
    isWindowOpen: bool
    devices: List[Device]

    def get_active_mode(self):

        mode = copy.deepcopy(super().get_active_mode())
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


class Zone(Heated):
    targetMinTemperature: float
    activeFunction: str
    rooms: List[Room]
    rbr: bool

    def get_active_mode(self):

        mode = copy.deepcopy(super().get_active_mode())
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


class DomesticHotWater(Heated):

    def get_active_mode(self):
        if self.operationMode == constant.WATER_HEATER_MODE_ON:
            return TimeProgramDaySetting(str(0), self.targetTemperature, constant.WATER_HEATER_MODE_ON)
        elif self.operationMode == constant.WATER_HEATER_MODE_OFF:
            return TimeProgramDaySetting(str(0), constant.WATER_HEATER_MIN_TEMP, constant.WATER_HEATER_MODE_OFF)
        elif self.operationMode == constant.WATER_HEATER_MODE_BOOST:
            return TimeProgramDaySetting(str(0), self.targetTemperature, constant.WATER_HEATER_MODE_BOOST)
        else:
            # Mode AUTO
            mode = copy.deepcopy(super().get_active_mode())
            if mode.mode == constant.WATER_HEATER_MODE_ON:
                mode.mode = constant.WATER_HEATER_MODE_AUTO_ON
                mode.temperature = self.targetTemperature
            else:
                mode.mode = constant.WATER_HEATER_MODE_AUTO_OFF
                mode.temperature = constant.WATER_HEATER_MIN_TEMP
            return mode


class Circulation(Heated):
    pass


class HolidayMode:
    active: bool
    startDate: date
    endDate: date
    configuredTemperature: float


class VaillantSystem:
    holidayMode: HolidayMode
    boilerStatus: BoilerStatus
    zones: List[Zone]
    dhw: DomesticHotWater
    #circulation: Circulation
    outdoorTemperature: float
    quickMode: QuickMode
