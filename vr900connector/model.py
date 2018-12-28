from datetime import datetime
from typing import Dict, List


class BoxStatus:
    onlineStatus: str
    updateStatus: str


class BoxDetails:
    ethernetMac: str
    ethernetWifi: str
    ethernetWifiAP: str
    firmwareVersion: str


class BoilerStatus:
    code: str
    description: str
    date: datetime


class Configuration:
    pass


class TimeProgramDaySetting:
    startTime: str
    setting: str


class TimeProgramDay:
    timeProgramDaySettings: List[TimeProgramDaySetting]


class TimeProgram:
    TimeProgramDays: Dict[str, TimeProgramDay]


class Heated:
    timeProgram: TimeProgram
    name: str
    currentTemperature: float
    configuredTemperature: float
    operationMode: str


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


class VaillantSetup:
    boilerStatus: BoilerStatus
    boxStatus: BoxStatus
    boxDetails: BoxDetails
    rooms: Dict[int, Room]
    zones: Dict[str, Zone]
    dhw: DomesticHotWater
    circulation: Circulation
    serialNumber: str
    name: str
    outsideTemperature: float





