from datetime import datetime, date
from typing import Dict, List


class BoxStatus:
    onlineStatus: str
    updateStatus: str


class BoxDetails:
    ethernetMac: str
    ethernetWifi: str
    ethernetWifiAP: str
    firmwareVersion: str
    serialNumber: str


class BoilerStatus:
    code: str
    description: str
    date: datetime
    currentTemperature: float
    waterPressure: float


class TimeProgramDaySetting:
    startTime: str
    temperature: float

    def __init__(self, start_time: str, temperature: float):
        self.startTime = start_time
        self.temperature = temperature


class TimeProgramDay:
    timeProgramDaySettings: List[TimeProgramDaySetting]

    def __init__(self):
        self.timeProgramDaySettings = dict()

    def add_setting(self, start_time: str, temperature: float):
        self.timeProgramDaySettings.append(TimeProgramDaySetting(start_time, temperature))


class TimeProgram:
    timeProgramDays: Dict[str, TimeProgramDay]

    def __init__(self):
        self.timeProgramDays = dict()

    def add_day(self, day: str, time_program_day: TimeProgramDay):
        self.timeProgramDays[day] = time_program_day


class Heated:
    name: str
    timeProgram: TimeProgram
    currentTemperature: float
    configuredTemperature: float
    operationMode: str
    remainingQuickVeto: int


class Zone(Heated):
    id: str
    activeMode: str


class Device:
    name: str
    sgtin: str
    deviceType: str
    isBatteryLow: bool
    isRadioOutOfReach: bool


class Room(Heated):
    index: int
    childLock: bool
    isWindowOpen: bool
    devices: List[Device]
    icon: str


class DomesticHotWater(Heated):
    activeMode: str


class Circulation:
    timeProgram: TimeProgram
    name: str
    operationMode: str
    activeMode: str


class HolidayMode:
    active: bool
    startDate: date
    endDate: date
    configuredTemperature: float


class VaillantSystem:
    holidayMode: HolidayMode
    boilerStatus: BoilerStatus
    boxStatus: BoxStatus
    boxDetails: BoxDetails
    rooms: Dict[int, Room]
    zones: Dict[str, Zone]
    dhw: DomesticHotWater
    circulation: Circulation
    name: str
    outsideTemperature: float

    def set_rooms(self, rooms: List[Room]):
        self.rooms = dict()
        for room in rooms:
            self.rooms[room.index] = room




