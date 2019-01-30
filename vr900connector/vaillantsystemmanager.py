import logging
from datetime import date

from .model import VaillantSystem, Room, Zone, DomesticHotWater
from .modelmapper import Mapper
from .apiconnector import ApiConnector
from . import constant

LOGGER = logging.getLogger('VaillantSystemManager')


class VaillantSystemManager:

    def __init__(self, user, password, smartphone_id=constant.DEFAULT_SMARTPHONE_ID,
                 base_url=constant.DEFAULT_BASE_URL, file_dir=constant.DEFAULT_FILES_DIR):
        self.__connector = ApiConnector(user, password, smartphone_id, base_url, file_dir)
        self.__mapper = Mapper()

    def get_system(self):
        try:
            self.__connector.autoCloseSession = False
            full_system = self.__connector.get_system_control()
            live_report = self.__connector.get_live_report()
            hvac_state = self.__connector.get_hvac_state()

            holiday_mode = self.__mapper.holiday_mode(full_system)
            boiler_status = self.__mapper.boiler_status(hvac_state, live_report)

            zones = self.__mapper.zones(full_system)

            for zone in zones:
                if zone.rbr:
                    raw_rooms = self.__connector.get_rooms()
                    rooms = self.__mapper.rooms(raw_rooms)
                    zone.rooms = rooms
                    break

            dhw = self.__mapper.domestic_hot_water(full_system, live_report)

            outdoorTemperature = self.__mapper.outdoor_temp(full_system)
            quickMode = self.__mapper.quick_mode(full_system)

            vaillant_system = VaillantSystem()
            vaillant_system.holidayMode = holiday_mode
            vaillant_system.boilerStatus = boiler_status
            vaillant_system.dhw = dhw
            vaillant_system.outdoorTemperature = outdoorTemperature
            vaillant_system.zones = zones
            vaillant_system.quickMode = quickMode

            return vaillant_system
        finally:
            self.__connector.close_session()

    def refresh_room(self, room: Room):
        self.__connector.autoCloseSession = True
        return self.__mapper.room(self.__connector.get_room(room.id))

    def refresh_rooms(self):
        self.__connector.autoCloseSession = True
        return self.__mapper.rooms(self.__connector.get_rooms())

    def refresh_zones(self):
        self.__connector.autoCloseSession = True
        return self.__mapper.zones(self.__connector.get_zones())

    def refresh_zone(self, zone: Zone):
        self.__connector.autoCloseSession = True
        return self.__mapper.zones(self.__connector.get_zone(zone.id))

    def set_away(self, start_date: date, end_date: date):
        """TODO if not provided, default date, one day ?"""
        pass

    def remove_away(self):
        """TODO """
        pass

    def set_dhw_setpoint_temperature(self, dhw: DomesticHotWater, temperature):
        LOGGER.info("Will try to set dhw target temperature to %s", temperature)
        if temperature:
            self.__connector.set_dhw_setpoint_temperature(dhw.id, round(float(temperature)))
            return True
        else:
            LOGGER.debug("No temperature provided, nothing to do")
            return False

    """
        Returns True/False whether new_mode has been set or not.
        Throw an error if something went wrong while setting new_mode
    """
    def set_dhw_operation_mode(self, sys: VaillantSystem, new_mode):
        LOGGER.info("Will try to set dhw mode to %s", new_mode)

        dhw = sys.dhw
        quick_mode = sys.quickMode
        if new_mode:
            if dhw.operationMode != new_mode:
                if quick_mode:
                    if new_mode != constant.WATER_HEATER_MODE_BOOST:
                        LOGGER.debug("Quick mode %s is running and will get kept, new mode will be set", quick_mode.name)
                        self.__connector.set_dhw_operation_mode(dhw.id, new_mode)
                        return True
                    else:
                        LOGGER.debug("Quick mode %s is running and new_mode is also quick mode, won't change",
                                     quick_mode.name)
                        return False
                else:
                    if new_mode == constant.WATER_HEATER_MODE_BOOST:
                        LOGGER.debug("No quick mode running, "
                                     "new_mode is a quick mode and will be applied for the whole system")
                        self.__connector.set_quick_mode(new_mode)
                        return True
                    else:
                        LOGGER.debug("No quick mode running, new_mode is a classic mode")
                        self.__connector.set_dhw_operation_mode(dhw.id, new_mode)
                        return True
            else:
                LOGGER.debug("Mode %s is the same as previous mode %s", new_mode, dhw.operationMode)
                return False
        else:
            LOGGER.debug("No new mode provided, nothing to do")
            return False
