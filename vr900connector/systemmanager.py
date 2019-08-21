"""Convenient manager to easily gets data from API."""
import logging
from datetime import date, timedelta
from typing import Optional, List

from .api import ApiConnector, urls, payloads, defaults, ApiError
from .model import mapper, System, HotWater, QuickMode, QuickVeto, Room, \
    Zone, OperationMode, Circulation, constants

_LOGGER = logging.getLogger('SystemManager')


# pylint: disable=too-many-public-methods
class SystemManager:
    """This is the main class to use if you want to do more advanced (and do
    it easily) things with your system.

    All the manager does is calling the *api connector* with correct *url*,
    *method* and *payload*.

    The manager is throwing *ApiError* without altering it
    """

    def __init__(self, user: str, password: str,
                 smartphone_id: str = defaults.SMARTPHONE_ID,
                 file_path: str = defaults.FILES_PATH):
        self._connector: ApiConnector = \
            ApiConnector(user, password, smartphone_id, file_path)

    def login(self, force_login: bool = False) -> bool:
        """Tries to login, return True/False.

        See *api connector* for details
        """
        return self._connector.login(force_login)

    # pylint: disable=too-many-locals
    def get_system(self) -> System:
        """Get the full system.

        This may be a bit slow because all calls to the API are sync for now.
        """
        full_system = self._connector.get(urls.system())
        live_report = self._connector.get(urls.live_report())
        hvac_state = self._connector.get(urls.hvac())

        holiday_mode = mapper.map_holiday_mode(full_system)
        boiler_status = mapper.map_boiler_status(hvac_state, live_report)
        system_status = mapper.map_system_status(hvac_state)

        zones = mapper.map_zones(full_system)

        rooms: List[Room] = []
        for zone in zones:
            if zone.rbr:
                rooms = mapper.map_rooms(self._connector.get(urls.rooms()))
                break

        hot_water = mapper.map_hot_water(full_system, live_report)
        circulation = mapper.map_circulation(full_system)

        outdoor_temp = mapper.map_outdoor_temp(full_system)
        quick_mode = mapper.map_quick_mode(full_system)
        errors = mapper.map_errors(hvac_state)

        return System(holiday_mode, system_status, boiler_status, zones, rooms,
                      hot_water, circulation, outdoor_temp, quick_mode, errors)

    def get_hot_water(self, dhw_id: str) -> Optional[HotWater]:
        """Get *hot water*."""

        full_system = self._connector.get(urls.hot_water(dhw_id))
        live_report = self._connector.get(urls.live_report())
        return mapper.map_hot_water_alone(full_system, dhw_id, live_report)

    def get_room(self, room_id: str) -> Optional[Room]:
        """Get *room*."""
        new_room = self._connector.get(urls.room(room_id))
        return mapper.map_room(new_room)

    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get *zone*."""
        new_zone = self._connector.get(urls.zone(zone_id))
        return mapper.map_zone(new_zone)

    def get_circulation(self, dhw_id: str) \
            -> Optional[Circulation]:
        """Get *circulation*."""
        new_circulation = self._connector.get(urls.circulation(dhw_id))
        return mapper.map_circulation_alone(new_circulation, dhw_id)

    def set_hot_water_setpoint_temperature(self, dhw_id: str,
                                           temperature: float) -> None:
        """This set the target temperature for *hot water*."""
        _LOGGER.debug("Will set dhw target temperature to %s",
                      temperature)
        self._connector.put(
            urls.hot_water_temperature_setpoint(dhw_id),
            payloads.hotwater_temperature_setpoint(self._round(temperature)))

    def set_hot_water_operation_mode(self, dhw_id: str,
                                     new_mode: OperationMode) -> None:
        """Set new operation mode for *hot water*."""
        _LOGGER.debug("Will try to set hot water mode to %s", new_mode)

        if new_mode in HotWater.MODES:
            _LOGGER.debug("New mode is %s", new_mode)
            self._connector.put(
                urls.hot_water_operation_mode(dhw_id),
                payloads.hot_water_operation_mode(new_mode.name))
        else:
            _LOGGER.debug("New mode is not available for hot water %s",
                          new_mode)

    def set_room_operation_mode(self, room_id: str, new_mode: OperationMode) \
            -> None:
        """Set new operation mode for a *room*."""
        if new_mode in Room.MODES and new_mode != OperationMode.QUICK_VETO:
            _LOGGER.debug("New mode is %s", new_mode)
            self._connector.put(urls.room_operation_mode(room_id),
                                payloads.room_operation_mode(
                                    new_mode.name))
        else:
            _LOGGER.debug("mode is not available for room %s", new_mode)

    def set_zone_operation_mode(self, zone_id: str, new_mode: OperationMode) \
            -> None:
        """Set new operation mode for a *zone*."""
        if new_mode in Zone.MODES and new_mode != OperationMode.QUICK_VETO:
            _LOGGER.debug("New mode is %s", new_mode)
            self._connector.put(urls.zone_heating_mode(zone_id),
                                payloads.zone_operation_mode(new_mode.name))
        else:
            _LOGGER.debug("mode is not available for zone %s", new_mode)

    def set_quick_mode(self, quick_mode: QuickMode) -> None:
        """Set *quick mode* system wise.

        **Please note that it will override the current quick mode, if any**
        """
        self._connector.put(urls.system_quickmode(),
                            payloads.quickmode(quick_mode.name))

    def remove_quick_mode(self) -> None:
        """Removes current *quick mode*.

        if there is not quick mode set, the API returns an error (HTTP 409).
        This error is swallowed by the manager."""
        try:
            self._connector.delete(urls.system_quickmode())
        except ApiError as exc:
            if exc.response is None or exc.response.status_code != 409:
                raise exc

    def set_room_quick_veto(self, room_id: str, quick_veto: QuickVeto) -> None:
        """Set a *quick veto* for the *room*.
        It will override the current *quick veto*, if any.
        """
        self._connector.put(urls.room_quick_veto(room_id),
                            payloads.room_quick_veto(
                                quick_veto.target_temperature,
                                quick_veto.remaining_time))

    def remove_room_quick_veto(self, room_id: str) -> None:
        """Remove the *quick veto* from a *room*."""
        self._connector.delete(urls.room_quick_veto(room_id))

    def set_zone_quick_veto(self, zone_id: str, quick_veto: QuickVeto) -> None:
        """Set a *quick veto* for the *zone*.
        It will override the current *quick veto*, if any.
        """
        self._connector.put(urls.zone_quick_veto(zone_id),
                            payloads.zone_quick_veto(
                                quick_veto.target_temperature))

    def remove_zone_quick_veto(self, zone_id: str) -> None:
        """Remove the *quick veto* from a *zone*."""
        self._connector.delete(urls.zone_quick_veto(zone_id))

    def set_room_setpoint_temperature(self, room_id: str, temperature: float) \
            -> None:
        """This set the *target temperature* for a *room*."""
        _LOGGER.debug("Will try to set room target temperature to %s",
                      temperature)
        self._connector.put(urls.room_set_temperature_setpoint(room_id),
                            payloads.room_temperature_setpoint(
                                self._round(temperature)))

    def set_zone_setpoint_temperature(self, zone_id: str, temperature: float) \
            -> None:
        """This set the *target temperature* for a *zone*."""
        _LOGGER.debug("Will try to set zone target temperature to %s",
                      temperature)
        self._connector.put(
            urls.zone_heating_setpoint_temperature(zone_id),
            payloads.zone_temperature_setpoint(self._round(temperature)))

    def set_zone_setback_temperature(self, zone_id: str, temperature: float) \
            -> None:
        """This set the *setback temperature* for a *zone*."""
        _LOGGER.debug("Will try to set zone setback temperature to %s",
                      temperature)
        self._connector.put(urls.zone_heating_setback_temperature(zone_id),
                            payloads.zone_temperature_setback(
                                self._round(temperature)))

    def set_holiday_mode(self, start_date: date, end_date: date,
                         temperature: float) -> None:
        """Set the holiday mode."""
        self._connector.put(urls.system_holiday_mode(),
                            payloads.holiday_mode(True, start_date, end_date,
                                                  temperature))

    def remove_holiday_mode(self, temperature: float =
                            constants.FROST_PROTECTION_TEMP) -> None:
        """Remove *holiday mode*.

        This is quite special since the API doesn't simply accept a DELETE, so
        the manager is setting the start date to two days before and end date
        to yesterday.
        """

        start_date = date.today() - timedelta(days=2)
        end_date = date.today() - timedelta(days=1)
        self._connector.put(urls.system_holiday_mode(),
                            payloads.holiday_mode(False, start_date, end_date,
                                                  temperature))

    def request_hvac_update(self) -> None:
        """Request an hvac update. This allow the vaillant API to read the data
        from your system.

        Please note, the **request** done by the manager is done
        **synchronously**, but the **update** requested is done
        **asynchronously** by vaillant API.

        This is necessary to update *boiler status* and *errors*.

        Please note it can take some times for the update to occur (Most of the
        time, it takes about 1 or 2 minutes before you can see changes)

        It the request is done too often, the API may return an error
        (HTTP 409).
        """

        state = mapper.map_hvac_sync_state(self._connector.get(urls.hvac()))

        if state and not state.is_pending:
            self._connector.put(urls.hvac_update())

    def logout(self) -> None:
        """Get logged out from the API"""
        self._connector.logout()

    # pylint: disable=no-self-use
    def _round(self, number: float) -> float:
        """round a float to the nearest 0.5, as vaillant API only accepts 0.5
        step"""
        return round(number * 2) / 2
