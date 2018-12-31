from datetime import datetime, date, timedelta
from typing import Dict, List


class BoxDetails:
    onlineStatus: str
    updateStatus: str
    ethernetMac: str
    wifiMac: str
    wifiAPMac: str
    firmwareVersion: str
    serialNumber: str


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
        hour = int(split[0]) * 60
        minute = int(split[1])
        return hour + minute


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
        return None


class QuickVeto:
    startTime: datetime
    remainingTime: int
    configuredTemperature: float

    def __init__(self, remaining_time: int, configured_temperature: float, start_time: datetime = None):
        self.remainingTime = remaining_time
        self.configuredTemperature = configured_temperature
        self.startTime = start_time


class Heated:
    id: str
    name: str
    timeProgram: TimeProgram
    currentTemperature: float
    configuredTemperature: float
    operationMode: str
    quickVeto: QuickVeto = None

    def get_active_mode(self):
        if self.quickVeto and self.quickVeto.remainingTime > 0:
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


class Zone(Heated):
    configuredMinTemperature: float
    activeFunction: str
    rooms: Dict[str, Room]
    rbr: bool

    def set_rooms(self, rooms: List[Room]):
        self.rooms = dict()
        for room in rooms:
            self.rooms[room.id] = room


class DomesticHotWater(Zone):
    pass


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
    boxDetails: BoxDetails
    zones: Dict[str, Zone]
    dhw: DomesticHotWater
    circulation: Circulation
    name: str
    outsideTemperature: float

    def set_zones(self, zones: List[Zone]):
        self.zones = dict()
        for zone in zones:
            self.zones[zone.id] = zone
