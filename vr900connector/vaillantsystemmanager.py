from .model import VaillantSystem, Room, Zone
from .modelmapper import Mapper
from .apiconnector import ApiConnector
from . import constant


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
            # facilities = self.__connector.get_facilities()
            # system_status = self.__connector.get_system_status()

            holiday_mode = self.__mapper.holiday_mode(full_system)
            boiler_status = self.__mapper.boiler_status(hvac_state, live_report)
            # box_detail = self.__mapper.box_detail(facilities, system_status)

            zones = self.__mapper.zones(full_system)

            for zone in zones:
                if zone.rbr:
                    raw_rooms = self.__connector.get_rooms()
                    rooms = self.__mapper.rooms(raw_rooms)
                    zone.rooms = rooms
                    break

            dhw = self.__mapper.domestic_hot_water(full_system, live_report)
            # circulation = self.__mapper.circulation(full_system)

            outdoorTemperature = self.__mapper.outdoor_temp(full_system)
            # installation_name = self.__mapper.installation_name(facilities)
            quickMode = self.__mapper.quick_mode(full_system)

            vaillant_system = VaillantSystem()
            vaillant_system.holidayMode = holiday_mode
            vaillant_system.boilerStatus = boiler_status
            vaillant_system.dhw = dhw
            # vaillant_system.circulation = circulation
            # vaillant_system.boxDetails = box_detail
            vaillant_system.outdoorTemperature = outdoorTemperature
            vaillant_system.zones = zones
            # vaillant_system.name = installation_name
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
