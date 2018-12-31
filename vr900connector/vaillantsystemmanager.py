from model import VaillantSystem, Zone, Room
from modelmapper import Mapper
from vr900connector.vr900connector import Vr900Connector
import constant


class VaillantSystemManager:

    def __init__(self, user, password, smartphone_id=constant.DEFAULT_SMARTPHONE_ID,
                 base_url=constant.DEFAULT_BASE_URL, file_dir=constant.DEFAULT_FILES_DIR):
        self.__connector = Vr900Connector(user, password, smartphone_id, base_url, file_dir)
        self.__mapper = Mapper()

    def get_system(self):
        full_system = self.__connector.get_system_control()
        live_report = self.__connector.get_live_report()
        hvac_state = self.__connector.get_hvac_state()
        facilities = self.__connector.get_facilities()
        system_status = self.__connector.get_system_status()

        raw_rooms = dict()
        room_by_room = "ROOM_BY_ROOM" in facilities.get("body", dict()).get("facilitiesList",
                                                                            list())[0].get("capabilities")
        if room_by_room:
            raw_rooms = self.__connector.get_rooms()

        holiday_mode = Mapper.holiday_mode(full_system)
        boiler_status = Mapper.boiler_status(hvac_state, live_report)
        box_detail = Mapper.box_detail(facilities, system_status)

        rooms = Mapper.rooms(raw_rooms)
        zones = Mapper.zones(full_system)
        if room_by_room:
            for zone in zones:
                if zone.rbr:
                    zone.set_rooms(rooms)
                    break

        dhw = Mapper.domestic_hot_water(full_system, live_report)
        circulation = Mapper.circulation(full_system)

        outsideTemp = full_system.get("body").get("status", dict()).get('outside_temperature')
        installation_name = facilities.get("body", dict()).get("facilitiesList", list())[0].get("name")

        vaillant_system = VaillantSystem()
        vaillant_system.holidayMode = holiday_mode
        vaillant_system.boilerStatus = boiler_status
        vaillant_system.dhw = dhw
        vaillant_system.circulation = circulation
        vaillant_system.boxDetails = box_detail
        vaillant_system.outsideTemperature = outsideTemp
        vaillant_system.set_zones(zones)
        vaillant_system.name = installation_name

        return vaillant_system

    def refresh_room(self, room: Room):
        rawRoom = self.__connector.get_room(room.id)
        return self.__mapper.room(rawRoom)

    def refresh_rooms(self):
        rawRoom = self.__connector.get_rooms()
        return self.__mapper.room(rawRoom)

    def refresh_zone(self, zone: Zone):
        self.__connector.get_zones()
        return zone
