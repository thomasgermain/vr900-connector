import logging

from .api import ApiConnector, urls, payloads
from .api.constants import DEFAULT_SMART_PHONE_ID, DEFAULT_FILES_PATH
from .model import Mapper, System, HotWater
from .model.constants import QM_HOTWATER_BOOST

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

    def __init__(self, user: str, password: str, smart_phone_id: str = DEFAULT_SMART_PHONE_ID,
                 file_path: str = DEFAULT_FILES_PATH):
        self._connector = ApiConnector(user, password, smart_phone_id, file_path)

    def get_system(self):
        full_system = self._connector.get(urls.system())
        live_report = self._connector.get(urls.live_report())
        hvac_state = self._connector.get(urls.hvac())

        holiday_mode = Mapper.holiday_mode(full_system)
        boiler_status = Mapper.boiler_status(hvac_state)

        zones = Mapper.zones(full_system)

        rooms = None
        for zone in zones:
            if zone.rbr:
                raw_rooms = self._connector.get(urls.rooms())
                rooms = Mapper.rooms(raw_rooms)
                break

        hot_water = Mapper.domestic_hot_water(full_system, live_report)
        circulation = Mapper.circulation(full_system)

        outdoorTemperature = Mapper.outdoor_temp(full_system)
        quickMode = Mapper.quick_mode(full_system)

        return System(holiday_mode, boiler_status, zones, rooms, hot_water, circulation, outdoorTemperature, quickMode)

    def get_hot_water(self):
        full_system = self._connector.get(urls.system())
        live_report = self._connector.get(urls.live_report())
        return Mapper.domestic_hot_water(full_system, live_report)

    def set_hot_water_setpoint_temperature(self, hot_water: HotWater, temperature: float):
        LOGGER.info("Will try to set dhw target temperature to %s", temperature)
        if temperature:
            self._connector.put(urls.set_hot_water_temperature_setpoint(hot_water.id),
                                payloads.set_temperature_setpoint(round(float(temperature))))
            return True
        else:
            LOGGER.debug("No temperature provided, nothing to do")
            return False

    def set_hot_water_operation_mode(self, system: System, new_mode: str):
        """
        Set new operation mode for the hot water system.

        :param system: the :class:`vr900connector.model.System` representing to current system
        :param new_mode: Name of the new mode, see :mod:`vr900connector.model.constants`
        :return: True/False whether new_mode has been set or not
        """
        LOGGER.info("Will try to set hot water mode to %s", new_mode)

        hot_water = system.hot_water
        quick_mode = system.quick_mode
        if new_mode:
            if hot_water.operation_mode != new_mode:
                if quick_mode:
                    if new_mode != QM_HOTWATER_BOOST:
                        LOGGER.debug("Quick mode %s is running and will get kept, new mode will be set",
                                     quick_mode.name)
                        return self._set_hot_water_operation_mode(hot_water, new_mode)
                    else:
                        LOGGER.debug("Quick mode %s is running and new_mode is also quick mode, won't change",
                                     quick_mode.name)
                        return False
                else:
                    if new_mode == QM_HOTWATER_BOOST:
                        LOGGER.debug("No quick mode running, "
                                     "new_mode is a quick mode and will be applied for the whole system")
                        return self.set_quick_mode(new_mode)
                    else:
                        LOGGER.debug("No quick mode running, new_mode is a classic mode")
                        self._set_hot_water_operation_mode(hot_water, new_mode)
                        return True
            else:
                LOGGER.debug("Mode %s is the same as previous mode %s", new_mode, hot_water.operation_mode)
                return False
        else:
            LOGGER.debug("No new mode provided, nothing to do")
            return False

    def set_quick_mode(self, quick_mode: str):
        """
        Set quick mode system wise
        :return: True if everything is ok
        """
        self._connector.put(urls.system_quickmode(), payloads.quickmode(quick_mode))
        return True

    def logout(self):
        """
        Get logged out from the API
        """
        self._connector.logout()

    def _set_hot_water_operation_mode(self, hot_water: HotWater, new_mode: str):
        self._connector.put(urls.set_hot_water_operation_mode(hot_water.id),
                            payloads.set_operation_mode(new_mode))
        return True
