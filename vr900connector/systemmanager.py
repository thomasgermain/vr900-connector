import logging
from datetime import date, timedelta

from .api import ApiConnector, Urls, Payloads, Defaults
from .model import Mapper, System, HotWater, QuickMode, QuickVeto, Room, Zone, HeatingMode, Circulation, Constants

LOGGER = logging.getLogger('SystemManager')


class SystemManager:
    """
    This is the main class to use if you want to do more advanced things with your system.

    The manager is throwing :exc:`vr900connector.api.ApiError` (thrown by :class:`vr900connector.api.ApiConnector`)
    without altering it

    Args:
        user: User for login
        password: Password for login
        smart_phone_id: Smart phone id required by the API
        file_path: Where to store files created by the underlying connector.
    """

    def __init__(self, user: str, password: str, smart_phone_id: str = Defaults.SMART_PHONE_ID,
                 file_path: str = Defaults.FILES_PATH):
        self._connector = ApiConnector(user, password, smart_phone_id, file_path)

    def get_system(self):
        full_system = self._connector.get(Urls.system())
        live_report = self._connector.get(Urls.live_report())
        hvac_state = self._connector.get(Urls.hvac())

        holiday_mode = Mapper.holiday_mode(full_system)
        boiler_status = Mapper.boiler_status(hvac_state, live_report)

        zones = Mapper.zones(full_system)

        rooms = None
        for zone in zones:
            if zone.rbr:
                raw_rooms = self._connector.get(Urls.rooms())
                rooms = Mapper.rooms(raw_rooms)
                break

        hot_water = Mapper.domestic_hot_water(full_system, live_report)
        circulation = Mapper.circulation(full_system)

        outdoorTemperature = Mapper.outdoor_temp(full_system)
        quickMode = Mapper.quick_mode(full_system)

        return System(holiday_mode, boiler_status, zones, rooms, hot_water, circulation, outdoorTemperature, quickMode)

    def get_hot_water(self, hot_water: HotWater):
        full_system = self._connector.get(Urls.hot_water(hot_water.id))
        live_report = self._connector.get(Urls.live_report())
        return Mapper.domestic_hot_water_alone(full_system, hot_water.id, live_report)

    def get_room(self, room: Room):
        new_room = self._connector.get(Urls.room(room.id))
        return Mapper.room(new_room)

    def get_zone(self, zone: Zone):
        new_zone = self._connector.get(Urls.zone(zone.id))
        return Mapper.zone(new_zone)

    def get_circulation(self, circulation: Circulation):
        new_circulation = self._connector.get(Urls.circulation(circulation.id))
        return Mapper.circulation_alone(new_circulation, circulation.id)

    def set_hot_water_setpoint_temperature(self, hot_water: HotWater, temperature: float):
        """
        This set the target temperature for the hotwater.

        :param hot_water: the hot_water you want to set target temperature
        :param temperature: the temperature
        :return: True/False whether the update occurred or not
        """
        LOGGER.info("Will try to set dhw target temperature to %s", temperature)
        if temperature and hot_water:
            self._connector.put(Urls.hot_water_temperature_setpoint(hot_water.id),
                                Payloads.hotwater_temperature_setpoint(round(float(temperature))))
            return True
        else:
            LOGGER.debug("No temperature nor hot_water provided, nothing to do")
            return False

    def set_hot_water_operation_mode(self, hotwater: HotWater, new_mode: HeatingMode):
        """
        Set new operation mode for the hot water.

        :param hotwater: the :class:`vr900connector.model.HotWater` representing to current hotwater component
        :param new_mode: Name of the new mode, see :mod:`vr900connector.model.HeatingMode`
        :return: True/False whether new_mode has been set or not
        """
        LOGGER.info("Will try to set hot water mode to %s", new_mode)

        if hotwater:
            if new_mode:
                if new_mode in HotWater.MODES:
                    LOGGER.debug("New mode is %s", new_mode)
                    self._connector.put(Urls.hot_water_operation_mode(hotwater.id),
                                        Payloads.hot_water_operation_mode(new_mode.name))
                    return True
                else:
                    LOGGER.debug("New mode is not available for hot water %s", new_mode)
                    return False
            else:
                LOGGER.debug("No new mode provided, nothing to do")
                return False
        else:
            LOGGER.debug("No hotwater provided")
            return False

    def set_room_operation_mode(self, room: Room, new_mode: HeatingMode):
        """
        Set new operation mode for a room.

        :param room: the :class:`vr900connector.model.Room` representing to current room component
        :param new_mode:
        :return: True/False whether new_mode has been set or not
        """

        if room:
            if new_mode:
                if new_mode in Room.MODES and new_mode != HeatingMode.QUICK_VETO:
                    LOGGER.debug("New mode is %s", new_mode)
                    self._connector.put(Urls.room_operation_mode(room.id), Payloads.room_operation_mode(new_mode.name))
                    return True
                else:
                    LOGGER.debug("New mode is not available for room %s", new_mode)
                    return False
            else:
                LOGGER.debug("No new mode provided, nothing to do")
                return False
        else:
            LOGGER.debug("No room provided")
            return False

    def set_zone_operation_mode(self, zone: Zone, new_mode: HeatingMode):
        """
        Set new operation mode for a zone.

        :param zone: the :class:`vr900connector.model.Zone` representing to current zone component
        :param new_mode:
        :return: True/False whether new_mode has been set or not
        """

        if zone:
            if new_mode:
                if new_mode in Zone.MODES and new_mode != HeatingMode.QUICK_VETO:
                    LOGGER.debug("New mode is %s", new_mode)
                    self._connector.put(Urls.zone_heating_mode(zone.id), Payloads.zone_operation_mode(new_mode.name))
                    return True
                else:
                    LOGGER.debug("New mode is not available for zone %s", new_mode)
                    return False
            else:
                LOGGER.debug("No new mode provided, nothing to do")
                return False
        else:
            LOGGER.debug("No zone provided")
            return False

    def set_quick_mode(self, current_quick_mode: QuickMode, new_quick_mode: QuickMode):
        """
        Set quick mode system wise
        :return: True/False whether new_mode has been set or not
        """

        if not current_quick_mode:
            if new_quick_mode:
                self._connector.put(Urls.system_quickmode(), Payloads.quickmode(new_quick_mode.name))
                return True
            else:
                LOGGER.debug("No new quick mode provided")
                return False
        else:
            LOGGER.debug("There is already a quick mode in place: %s", current_quick_mode.name)
            return False

    def set_room_quick_veto(self, room: Room, quick_veto: QuickVeto):
        if quick_veto and room:
            self._connector.put(Urls.room_quick_veto(room.id),
                                Payloads.room_quick_veto(quick_veto.target_temperature, quick_veto.remaining_time))
            return True
        else:
            LOGGER.debug("Quick veto %s or room %s not provided", quick_veto, room)
            return False

    def remove_room_quick_veto(self, room: Room):
        self._connector.delete(Urls.room_quick_veto(room.id))
        return True

    def set_zone_quick_veto(self, zone: Zone, quick_veto: QuickVeto):
        if quick_veto and zone:
            self._connector.put(Urls.zone_quick_veto(zone.id),
                                Payloads.zone_quick_veto(quick_veto.target_temperature))
            return True
        else:
            LOGGER.debug("Quick veto %s or zone %s not provided", quick_veto, zone)
            return False

    def remove_zone_quick_veto(self, zone: Zone):
        self._connector.delete(Urls.zone_quick_veto(zone.id))
        return True

    def set_room_setpoint_temperature(self, room: Room, temperature: float):
        """
        This set the target temperature for a room.

        :param room: the room you want to set target temperature
        :param temperature: the temperature
        :return: True/False whether the update occurred or not
        """
        LOGGER.info("Will try to set room target temperature to %s", temperature)
        if temperature and room:
            self._connector.put(Urls.room_set_temperature_setpoint(room.id),
                                Payloads.room_temperature_setpoint(round(float(temperature))))
            return True
        else:
            LOGGER.debug("No temperature nor room provided, nothing to do")
            return False

    def set_zone_setpoint_temperature(self, zone: Zone, temperature: float):
        """
        This set the target temperature for a zone.

        :param zone: the zone you want to set target temperature
        :param temperature: the temperature
        :return: True/False whether the update occurred or not
        """
        LOGGER.info("Will try to set zone target temperature to %s", temperature)
        if temperature and zone:
            self._connector.put(Urls.zone_heating_setpoint_temperature(zone.id),
                                Payloads.zone_temperature_setpoint(round(float(temperature))))
            return True
        else:
            LOGGER.debug("No temperature nor zone provided, nothing to do")
            return False

    def set_zone_setback_temperature(self, zone: Zone, temperature: float):
        """
        This set the setback temperature for a zone.

        :param zone: the zone you want to set setback temperature
        :param temperature: the temperature
        :return: True/False whether the update occurred or not
        """
        LOGGER.info("Will try to set zone setback temperature to %s", temperature)
        if temperature and zone:
            self._connector.put(Urls.zone_heating_setback_temperature(zone.id),
                                Payloads.zone_temperature_setback(round(float(temperature))))
            return True
        else:
            LOGGER.debug("No temperature nor zone provided, nothing to do")
            return False

    def set_holiday_mode(self, start_date: date, end_date: date, temperature: float):
        """
        Set the holiday mode

        :param start_date: starting date of the holiday mode
        :param end_date: ending date of the holiday mode
        :param temperature: minimal temperature
        :return: True if update occurred
        """
        self._connector.put(Urls.system_holiday_mode(), Payloads.holiday_mode(True, start_date, end_date, temperature))
        return True

    def remove_holiday_mode(self, temperature: float = Constants.FROST_PROTECTION_TEMP):
        """
        Remove holiday mode. Set start date to two days before and end date to yesterday

        :param temperature: default is :class:`vr900connector.model.Constants#FROST_PROTECTION_TEMP`
        :return: True if update occurred
        """
        self._connector.put(Urls.system_holiday_mode(), Payloads.holiday_mode(False,
                                                                              date.today() - timedelta(days=2),
                                                                              date.today() - timedelta(days=1),
                                                                              temperature))
        return True

    def request_hvac_update(self):
        """
        Request an hvac update. Please note the update is done asynchronously. Most of the time, it takes about 1 or 2
        minutes before you can see the new status in :class:`vr900connector.model.BoilerStatus`
        :return: True if the update request was accepted by the API
        """
        self._connector.put(Urls.hvac_update())
        return True

    def logout(self):
        """
        Get logged out from the API
        """
        self._connector.logout()
