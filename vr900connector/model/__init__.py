"""Mapped model from the API."""
# pylint: disable=cyclic-import
from .mode import Mode, OperatingMode, OperatingModes, QuickMode, QuickModes, \
    QuickVeto, HolidayMode, ActiveMode, SettingMode
from .timeprogram import TimeProgram, TimeProgramDay, TimePeriodSetting
from .component import Component, Circulation, HotWater, Device, Room, Zone
from .status import BoilerStatus, SystemStatus
from .error import Error
from .system import System
from .syncstate import SyncState
