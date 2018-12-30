from typing import List

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
        livereport = self.__connector.get_live_report()
        hvac_state = self.__connector.get_hvac_state()
        facilities = self.__connector.get_facilities()
        system_status = self.__connector.get_system_status()

        raw_rooms = dict()
        raw_zones = dict()
        if "ROOM_BY_ROOM" in facilities.get("body", dict()).get("facilitiesList", list())[0].get("capabilities"):
            raw_rooms = self.__connector.get_rooms()
            raw_zones = self.__filter_zones(full_system.get("body").get("zones"))

        holiday_mode = None
        if full_system.get("body").get("configuration", dict()).get("holidaymode", dict()).get("active", False):
            holiday_mode = Mapper.holiday_mode(full_system["body"]["configuration"]["holidaymode"])

        Mapper.boiler_status(hvac_state, livereport)
        Mapper.box_status(system_status)
        Mapper.box_detail(facilities)
        rooms = Mapper.rooms(raw_rooms)
        zones = Mapper.zones(raw_zones)
        Mapper.domestic_hot_water(full_system, livereport)
        Mapper.circulation(full_system)

        outsideTemp = full_system.get("body").get("status", dict()).get('outside_temperature')
        installation_name = facilities.get("body", dict()).get("facilitiesList", list())[0].get("name")

        vaillant_system = VaillantSystem()
        vaillant_system.set_rooms(rooms)
        return vaillant_system

    def refresh_room(self, room: Room):
        rawRoom = self.__connector.get_room(room.index)
        return self.__mapper.room(rawRoom)

    def refresh_rooms(self):
        rawRoom = self.__connector.get_rooms()
        return self.__mapper.room(rawRoom)

    def refresh_zone(self, zone: Zone):
        self.__connector.get_zones()
        return zone

    """
        Remove Zone controlled by RBR (room by room). This mean the zone is irrelevant and time program and 
        temperatures settings will be overridden by rooms
    """
    def __filter_zones(self, zones):
        filteredZone = list()
        if zones is not None:
            for zone in zones:
                if zone.get("currently_controlled_by") is None:
                    filteredZone.append(zone)

        return filteredZone
