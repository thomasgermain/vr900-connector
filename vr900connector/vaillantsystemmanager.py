import logging
from datetime import date

from .model.constant import QM_HOTWATER_BOOST
from .model import Room, Zone
from .model import Mapper
from .api import ApiConnector
from .api.constant import DEFAULT_SMARTPHONE_ID, DEFAULT_BASE_URL, DEFAULT_FILES_DIR
from .model import System, HotWater

LOGGER = logging.getLogger('VaillantSystemManager')


class VaillantSystemManager:

    __connector: ApiConnector = None

    def __init__(self, user, password, smartphone_id=DEFAULT_SMARTPHONE_ID,
                 base_url=DEFAULT_BASE_URL, file_dir=DEFAULT_FILES_DIR):
        self.__connector = ApiConnector(user, password, smartphone_id, base_url, file_dir)

    def get_system(self):
        try:
            self.__connector.autoCloseSession = False
            full_system = self.__connector.get_system_control()
            live_report = self.__connector.get_live_report()
            hvac_state = self.__connector.get_hvac_state()

            holiday_mode = Mapper.holiday_mode(full_system)
            boiler_status = Mapper.boiler_status(hvac_state, live_report)

            zones = Mapper.zones(full_system)

            for zone in zones:
                if zone.rbr:
                    raw_rooms = self.__connector.get_rooms()
                    rooms = Mapper.rooms(raw_rooms)
                    zone.rooms = rooms
                    break

            hot_water = Mapper.domestic_hot_water(full_system, live_report)
            circulation = Mapper.circulation(full_system)

            outdoorTemperature = Mapper.outdoor_temp(full_system)
            quickMode = Mapper.quick_mode(full_system)

            vaillant_system = System(holiday_mode, boiler_status, zones, hot_water, circulation,
                                     outdoorTemperature, quickMode)

            return vaillant_system
        finally:
            self.__connector.close_session()

    def get_hot_water(self):
        full_system = self.__connector.get_system_control()
        live_report = self.__connector.get_live_report()
        return Mapper.domestic_hot_water(full_system, live_report)

    def refresh_room(self, room: Room):
        self.__connector.autoCloseSession = True
        return Mapper.room(self.__connector.get_room(room.id))

    def refresh_rooms(self):
        self.__connector.autoCloseSession = True
        return Mapper.rooms(self.__connector.get_rooms())

    def refresh_zones(self):
        self.__connector.autoCloseSession = True
        return Mapper.zones(self.__connector.get_zones())

    def refresh_zone(self, zone: Zone):
        self.__connector.autoCloseSession = True
        return Mapper.zones(self.__connector.get_zone(zone.id))

    def set_away(self, start_date: date, end_date: date):
        """TODO if not provided, default date, one day ?"""
        pass

    def remove_away(self):
        """TODO """
        pass

    def set_hot_water_setpoint_temperature(self, hot_water: HotWater, temperature):
        LOGGER.info("Will try to set dhw target temperature to %s", temperature)
        if temperature:
            self.__connector.set_hot_water_operation_mode(hot_water.id, round(float(temperature)))
            return True
        else:
            LOGGER.debug("No temperature provided, nothing to do")
            return False

    """
        Returns True/False whether new_mode has been set or not.
        Throw an error if something went wrong while setting new_mode
    """

    def set_hot_water_operation_mode(self, system: System, new_mode):
        LOGGER.info("Will try to set hot water mode to %s", new_mode)

        hot_water = system.hotWater
        quick_mode = system.quickMode
        if new_mode:
            if hot_water.operationMode != new_mode:
                if quick_mode:
                    if new_mode != QM_HOTWATER_BOOST:
                        LOGGER.debug("Quick mode %s is running and will get kept, new mode will be set",
                                     quick_mode.boostMode.name)
                        self.__connector.set_hot_water_operation_mode(hot_water.id, new_mode)
                        return True
                    else:
                        LOGGER.debug("Quick mode %s is running and new_mode is also quick mode, won't change",
                                     quick_mode.boostMode.name)
                        return False
                else:
                    if new_mode == QM_HOTWATER_BOOST:
                        LOGGER.debug("No quick mode running, "
                                     "new_mode is a quick mode and will be applied for the whole system")
                        self.__connector.set_quick_mode(new_mode)
                        return True
                    else:
                        LOGGER.debug("No quick mode running, new_mode is a classic mode")
                        self.__connector.set_hot_water_operation_mode(hot_water.id, new_mode)
                        return True
            else:
                LOGGER.debug("Mode %s is the same as previous mode %s", new_mode, hot_water.operationMode)
                return False
        else:
            LOGGER.debug("No new mode provided, nothing to do")
            return False

    def logout(self):
        self.__connector.logout()
