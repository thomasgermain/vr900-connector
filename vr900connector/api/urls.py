class Urls:
    """
    Vaillant API Urls with placeholder when needed.
    All placeholders are resolved here except {serial_number} which is resolved by
    :class:`vr900connector.api.ApiConnector`
    """

    _BASE = 'https://smart.vaillant.com/mobile/api/v4'

    _BASE_AUTHENTICATE = _BASE + '/account/authentication/v1'
    _AUTHENTICATE = _BASE_AUTHENTICATE + '/authenticate'
    _NEW_TOKEN = _BASE_AUTHENTICATE + '/token/new'
    _LOGOUT = _BASE_AUTHENTICATE + '/logout'

    """Facility details"""
    _FACILITIES_LIST = _BASE + '/facilities'
    _FACILITIES = _FACILITIES_LIST + '/{serial_number}'
    _FACILITIES_DETAILS = _FACILITIES + '/system/v1/details'
    _FACILITIES_STATUS = _FACILITIES + '/system/v1/status'
    _FACILITIES_SETTINGS = _FACILITIES + '/storage'
    _FACILITIES_DEFAULT_SETTINGS = _FACILITIES + '/storage/default'
    _FACILITIES_INSTALLER_INFO = _FACILITIES + '/system/v1/installerinfo'

    """Rbr (Room by room)"""
    _RBR_BASE = _FACILITIES + '/rbr/v1'
    _RBR_INSTALLATION_STATUS = _RBR_BASE + '/installationStatus'
    _RBR_UNDERFLOOR_HEATING_STATUS = _RBR_BASE + '/underfloorHeatingStatus'

    """Rooms"""
    _ROOMS_LIST = _RBR_BASE + '/rooms'
    _ROOM = _ROOMS_LIST + '/{room_index}'
    _ROOM_CONFIGURATION = _ROOMS_LIST + '/{room_index}/configuration'
    _ROOM_QUICK_VETO = _ROOM_CONFIGURATION + '/quickVeto'
    _ROOM_TIMEPROGRAM = _ROOMS_LIST + '/{room_index}/timeprogram'
    _ROOM_OPERATION_MODE = _ROOM_CONFIGURATION + '/operationMode'
    _ROOM_CHILD_LOCK = _ROOM_CONFIGURATION + '/childLock'
    _ROOM_NAME = _ROOM_CONFIGURATION + '/name'
    _ROOM_DEVICE_NAME = _ROOM_CONFIGURATION + '/devices/{sgtin}/name'
    _ROOM_TEMPERATURE_SETPOINT = _ROOM_CONFIGURATION + '/temperatureSetpoint'

    """Repeaters"""
    _REPEATERS_LIST = _RBR_BASE + '/repeaters'
    _REPEATER_DELETE = _REPEATERS_LIST + '/{sgtin}'
    _REPEATER_SET_NAME = _REPEATERS_LIST + '/{sgtin}/name'

    """HVAC (heating, ventilation and Air-conditioning)"""
    _HVAC = _FACILITIES + '/hvacstate/v1/overview'
    _HVAC_REQUEST_UPDATE = _FACILITIES + '/hvacstate/v1/hvacMessages/update'

    """EMF (Embedded Metering Function)"""
    _LIVE_REPORT = _FACILITIES + '/livereport/v1'
    _LIVE_REPORT_DEVICE = _LIVE_REPORT + '/devices/{device_id}/reports/{report_id}'
    _PHOTOVOLTAICS_REPORT = _FACILITIES + '/spine/v1/currentPVMeteringInfo'
    _EMF_REPORT = _FACILITIES + '/emf/v1/devices'
    _EMF_REPORT_DEVICE = _EMF_REPORT + '/{device_id}'

    """System control"""
    _SYSTEM = _FACILITIES + '/systemcontrol/v1'
    _SYSTEM_CONFIGURATION = _SYSTEM + '/configuration'
    _SYSTEM_STATUS = _SYSTEM + '/status'
    _SYSTEM_DATETIME = _SYSTEM_STATUS + '/datetime'
    _SYSTEM_PARAMETERS = _SYSTEM + '/parameters'
    _SYSTEM_QUICK_MODE = _SYSTEM_CONFIGURATION + '/quickmode'
    _SYSTEM_HOLIDAY_MODE = _SYSTEM_CONFIGURATION + '/holidaymode'

    """DHW (Domestic Hot Water)"""
    _DHW = _SYSTEM + '/dhw/{dhw_id}'

    """Circulation"""
    _CIRCULATION = _DHW + '/circulation'
    _CIRCULATION_CONFIGURATION = _CIRCULATION + '/configuration'
    _CIRCULATION_TIMEPROGRAM = _CIRCULATION_CONFIGURATION + '/timeprogram'

    """Hot water"""
    _HOT_WATER = _DHW + '/hotwater'
    _HOT_WATER_CONFIGURATION = _HOT_WATER + '/configuration'
    _HOT_WATER_TIMEPROGRAM = _HOT_WATER_CONFIGURATION + '/timeprogram'
    _HOT_WATER_OPERATION_MODE = _HOT_WATER_CONFIGURATION + '/operation_mode'
    _HOT_WATER_TEMPERATURE_SETPOINT = _HOT_WATER_CONFIGURATION + '/temperature_setpoint'

    """Ventilation"""
    _VENTILATION = _SYSTEM + '/ventilation/{ventilation_id}'
    _VENTILATION_CONFIGURATION = _VENTILATION + '/fan/configuration'
    _VENTILATION_TIMEPROGRAM = _VENTILATION_CONFIGURATION + '/timeprogram'
    _VENTILATION_DAY_LEVEL = _VENTILATION_CONFIGURATION + '/day_level'
    _VENTILATION_NIGHT_LEVEL = _VENTILATION_CONFIGURATION + '/night_level'
    _VENTILATION_OPERATION_MODE = _VENTILATION_CONFIGURATION + '/operation_mode'

    """Zones"""
    _ZONES_LIST = _SYSTEM + '/zones'
    _ZONE = _ZONES_LIST + '/{zone_id}'
    _ZONE_CONFIGURATION = _ZONE + '/configuration'
    _ZONE_NAME = _ZONE_CONFIGURATION + '/name'
    _ZONE_QUICK_VETO = _ZONE_CONFIGURATION + '/quick_veto'

    """Zone heating"""
    _ZONE_HEATING_CONFIGURATION = _ZONE + '/heating/configuration'
    _ZONE_HEATING_TIMEPROGRAM = _ZONE + '/heating/timeprogram'
    _ZONE_HEATING_MODE = _ZONE_HEATING_CONFIGURATION + '/mode'
    _ZONE_HEATING_SETPOINT_TEMPERATURE = _ZONE_HEATING_CONFIGURATION + '/setpoint_temperature'
    _ZONE_HEATING_SETBACK_TEMPERATURE = _ZONE_HEATING_CONFIGURATION + '/setback_temperature'

    """Zone cooling"""
    _ZONE_COOLING_CONFIGURATION = _ZONE + '/cooling/configuration'
    _ZONE_COOLING_TIMEPROGRAM = _ZONE + '/cooling/timeprogram'
    _ZONE_COOLING_MODE = _ZONE_COOLING_CONFIGURATION + '/mode'
    _ZONE_COOLING_SETPOINT_TEMPERATURE = _ZONE_COOLING_CONFIGURATION + '/setpoint_temperature'
    _ZONE_COOLING_MANUAL_SETPOINT_TEMPERATURE = _ZONE_COOLING_CONFIGURATION + \
        '/manual_mode_cooling_temperature_setpoint'

    @classmethod
    def new_token(cls) -> str:
        """
        Url to request a new token.
        """
        return Urls._NEW_TOKEN

    @classmethod
    def authenticate(cls) -> str:
        """
        Url to authenticate the user and receive cookies.
        """
        return Urls._AUTHENTICATE

    @classmethod
    def logout(cls) -> str:
        """
        Url to logout from the application, cookies are invalidated.
        """
        return Urls._LOGOUT

    @classmethod
    def facilities_list(cls) -> str:
        """
        Url to get the list of serial numbers of the facilities (and some other properties). For now, the connector only
        handle one serial number.
        """
        return Urls._FACILITIES_LIST

    @classmethod
    def rbr_underfloor_heating_status(cls) -> str:
        """
        Url to check if underfloor heating is installed or not
        """
        return Urls._RBR_UNDERFLOOR_HEATING_STATUS.format(serial_number='{serial_number}')

    @classmethod
    def rbr_installation_status(cls) -> str:
        """
        Url to check installation status
        """
        return Urls._RBR_INSTALLATION_STATUS.format(serial_number='{serial_number}')

    @classmethod
    def rooms(cls) -> str:
        """
        Url to get the list of rooms
        """
        return Urls._ROOMS_LIST.format(serial_number='{serial_number}')

    @classmethod
    def room(cls, room_index: int) -> str:
        """
        Url to get specific room details (configuration, timeprogram)
        """
        return Urls._ROOM.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_configuration(cls, room_index: int) -> str:
        """
        Url to get configuration for a room (name, temperature, target temperature, etc.)
        """
        return Urls._ROOM_CONFIGURATION.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_quick_veto(cls, room_index: int) -> str:
        """
        Url to get configuration for a room (name, temperature, target temperature, etc.)
        """
        return Urls._ROOM_QUICK_VETO.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_operation_mode(cls, room_index: int) -> str:
        """
        Url to set operation for a room
        """
        return Urls._ROOM_OPERATION_MODE.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_timeprogram(cls, room_index: int) -> str:
        """
        Url to get configuration for a room (name, temperature, target temperature, etc.)
        """
        return Urls._ROOM_TIMEPROGRAM.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_set_child_lock(cls, room_index: int) -> str:
        """
        Url to set child lock for all devices in a room.
        """
        return Urls._ROOM_CHILD_LOCK.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_set_name(cls, room_index: int) -> str:
        """
        Url to set child lock for all devices in a room.
        """
        return Urls._ROOM_NAME.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def room_set_device_name(cls, room_index: int, sgtin) -> str:
        """
        Url to set child lock for all devices in a room.
        """
        return Urls._ROOM_DEVICE_NAME.format(serial_number='{serial_number}', room_index=room_index, sgtin=sgtin)

    @classmethod
    def room_set_temperature_setpoint(cls, room_index: int) -> str:
        """
        Url to set child lock for all devices in a room.
        """
        return Urls._ROOM_TEMPERATURE_SETPOINT.format(serial_number='{serial_number}', room_index=room_index)

    @classmethod
    def repeaters(cls) -> str:
        """
        Url to get list of repeaters
        """
        return Urls._REPEATERS_LIST.format(serial_number='{serial_number}')

    @classmethod
    def delete_repeater(cls, sgtin) -> str:
        """
        Url to delete a repeater
        """
        return Urls._REPEATER_DELETE.format(serial_number='{serial_number}', sgtin=sgtin)

    @classmethod
    def set_repeater_name(cls, sgtin) -> str:
        """
        Url to set repeater's name
        """
        return Urls._REPEATER_SET_NAME.format(serial_number='{serial_number}', sgtin=sgtin)

    @classmethod
    def hvac(cls) -> str:
        """
        Url of the hvac overview
        """
        return Urls._HVAC.format(serial_number='{serial_number}')

    @classmethod
    def hvac_update(cls) -> str:
        """
        Url to request hvac update
        """
        return Urls._HVAC_REQUEST_UPDATE.format(serial_number='{serial_number}')

    @classmethod
    def live_report(cls) -> str:
        """
        Url to get live report data (current boiler water temperature, current hot water temperature, etc.)
        """
        return Urls._LIVE_REPORT.format(serial_number='{serial_number}')

    @classmethod
    def live_report_device(cls, device_id, report_id) -> str:
        """
        Url to get live report for specific device
        """
        return Urls._LIVE_REPORT_DEVICE.format(serial_number='{serial_number}', device_id=device_id,
                                               report_id=report_id)

    @classmethod
    def photovoltaics(cls) -> str:
        """
        Url to get photovoltaics data
        """
        return Urls._PHOTOVOLTAICS_REPORT.format(serial_number='{serial_number}')

    @classmethod
    def emf_report(cls) -> str:
        """
        Url to get emf (Embedded Metering Function) report
        """
        return Urls._EMF_REPORT.format(serial_number='{serial_number}')

    @classmethod
    def emf_report_device(cls, device_id) -> str:
        """
        Url to get emf (Embedded Metering Function) report for a specific device
        """
        return Urls._EMF_REPORT_DEVICE.format(serial_number='{serial_number}', device_id=device_id)

    @classmethod
    def facilities_details(cls) -> str:
        """
        Url to get facility detail
        """
        return Urls._FACILITIES_DETAILS.format(serial_number='{serial_number}')

    @classmethod
    def facilities_status(cls) -> str:
        """
        Url to get facility status
        """
        return Urls._FACILITIES_STATUS.format(serial_number='{serial_number}')

    @classmethod
    def facilities_settings(cls) -> str:
        """
        Url to get facility settings
        """
        return Urls._FACILITIES_SETTINGS.format(serial_number='{serial_number}')

    @classmethod
    def facilities_default_settings(cls) -> str:
        """
        Url to get facility default settings
        """
        return Urls._FACILITIES_DEFAULT_SETTINGS.format(serial_number='{serial_number}')

    @classmethod
    def facilities_installer_info(cls) -> str:
        """
        Url to get facility default settings
        """
        return Urls._FACILITIES_INSTALLER_INFO.format(serial_number='{serial_number}')

    @classmethod
    def system(cls) -> str:
        """
        Url to get full system (zones, dhw, ventilation, holiday mode, etc.) except rooms
        """
        return Urls._SYSTEM.format(serial_number='{serial_number}')

    @classmethod
    def system_configuration(cls) -> str:
        """
        Url to get system configuration (holiday mode, quick mode etc.)
        """
        return Urls._SYSTEM_CONFIGURATION.format(serial_number='{serial_number}')

    @classmethod
    def system_status(cls) -> str:
        """
        Url to get outdoor temperature and datetime
        """
        return Urls._SYSTEM_STATUS.format(serial_number='{serial_number}')

    @classmethod
    def system_datetime(cls) -> str:
        """
        Url to set datetime
        """
        return Urls._SYSTEM_DATETIME.format(serial_number='{serial_number}')

    @classmethod
    def system_parameters(cls) -> str:
        """
        Url to get system control parameters
        """
        return Urls._SYSTEM_PARAMETERS.format(serial_number='{serial_number}')

    @classmethod
    def system_quickmode(cls) -> str:
        """
        Url to get system control quick mode
        """
        return Urls._SYSTEM_QUICK_MODE.format(serial_number='{serial_number}')

    @classmethod
    def system_holiday_mode(cls) -> str:
        """
        Url to get system control holiday mode
        """
        return Urls._SYSTEM_HOLIDAY_MODE.format(serial_number='{serial_number}')

    @classmethod
    def dhw(cls, dhw_id) -> str:
        """
        Url to get domestic hot water (hot water and circulation)
        """
        return Urls._DHW.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def circulation(cls, dhw_id) -> str:
        """
        Url to get circulation details
        """
        return Urls._CIRCULATION.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def circulation_configuration(cls, dhw_id) -> str:
        """
        Url to get circulation configuration
        """
        return Urls._CIRCULATION_CONFIGURATION.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def circulation_timeprogram(cls, dhw_id) -> str:
        """
        Url to get circulation timeprogram
        """
        return Urls._CIRCULATION_TIMEPROGRAM.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def hot_water(cls, dhw_id) -> str:
        """
        Url to get hot water detail
        """
        return Urls._HOT_WATER.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def hot_water_configuration(cls, dhw_id) -> str:
        """
        Url to get hot water configuration
        """
        return Urls._HOT_WATER_CONFIGURATION.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def hot_water_timeprogram(cls, dhw_id) -> str:
        """
        Url to get hot water timeprogram
        """
        return Urls._HOT_WATER_TIMEPROGRAM.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def hot_water_operation_mode(cls, dhw_id) -> str:
        """
        Url to set hot water operation mode, only if it's not a quick action
        """
        return Urls._HOT_WATER_OPERATION_MODE.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def hot_water_temperature_setpoint(cls, dhw_id) -> str:
        """
        Url to set hot water temperature setpoint
        """
        return Urls._HOT_WATER_TEMPERATURE_SETPOINT.format(serial_number='{serial_number}', dhw_id=dhw_id)

    @classmethod
    def ventilation(cls, ventilation_id) -> str:
        """
        Url to get ventilation details
        """
        return Urls._VENTILATION.format(serial_number='{serial_number}', ventilation_id=ventilation_id)

    @classmethod
    def ventilation_configuration(cls, ventilation_id) -> str:
        """
        Url to get ventilation configuration
        """
        return Urls._VENTILATION_CONFIGURATION.format(serial_number='{serial_number}', ventilation_id=ventilation_id)

    @classmethod
    def ventilation_timeprogram(cls, ventilation_id) -> str:
        """
        Url to get ventilation timeprogram
        """
        return Urls._VENTILATION_TIMEPROGRAM.format(serial_number='{serial_number}', ventilation_id=ventilation_id)

    @classmethod
    def set_ventilation_day_level(cls, ventilation_id) -> str:
        """
        Url to set ventilation day level
        """
        return Urls._VENTILATION_DAY_LEVEL.format(serial_number='{serial_number}', ventilation_id=ventilation_id)

    @classmethod
    def set_ventilation_night_level(cls, ventilation_id) -> str:
        """
        Url to set ventilation night level
        """
        return Urls._VENTILATION_NIGHT_LEVEL.format(serial_number='{serial_number}', ventilation_id=ventilation_id)

    @classmethod
    def set_ventilation_operation_mode(cls, ventilation_id) -> str:
        """
        Url to set ventilation operation mode
        """
        return Urls._VENTILATION_OPERATION_MODE.format(serial_number='{serial_number}', ventilation_id=ventilation_id)

    @classmethod
    def zones(cls) -> str:
        """
        Url to get zones
        """
        return Urls._ZONES_LIST.format(serial_number='{serial_number}')

    @classmethod
    def zone(cls, zone_id) -> str:
        """
        Url to get a specific zone
        """
        return Urls._ZONE.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_configuration(cls, zone_id) -> str:
        """
        Url to get a specific zone configuration
        """
        return Urls._ZONE_CONFIGURATION.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_name(cls, zone_id) -> str:
        """
        Url to set zone name
        """
        return Urls._ZONE_NAME.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_quick_veto(cls, zone_id) -> str:
        """
        Url to get quick veto
        """
        return Urls._ZONE_QUICK_VETO.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_heating_configuration(cls, zone_id) -> str:
        """
        Url to get zone heating configuration
        """
        return Urls._ZONE_HEATING_CONFIGURATION.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_heating_timeprogram(cls, zone_id) -> str:
        """
        Url to get a zone heating timeprogram
        """
        return Urls._ZONE_HEATING_TIMEPROGRAM.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_heating_mode(cls, zone_id) -> str:
        """
        Url to get a zone heating mode
        """
        return Urls._ZONE_HEATING_MODE.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_heating_setpoint_temperature(cls, zone_id) -> str:
        """
        Url to set a zone setpoint temperature
        """
        return Urls._ZONE_HEATING_SETPOINT_TEMPERATURE.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_heating_setback_temperature(cls, zone_id) -> str:
        """
        Url to set a zone setback temperature
        """
        return Urls._ZONE_HEATING_SETBACK_TEMPERATURE.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_cooling_configuration(cls, zone_id) -> str:
        """
        Url to get a zone cooling configuration
        """
        return Urls._ZONE_COOLING_CONFIGURATION.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_cooling_timeprogram(cls, zone_id) -> str:
        """
        Url to get zone cooling timeprogram
        """
        return Urls._ZONE_COOLING_TIMEPROGRAM.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_cooling_mode(cls, zone_id) -> str:
        """
        Url to set a zone cooling mode
        """
        return Urls._ZONE_COOLING_MODE.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_cooling_setpoint_temperature(cls, zone_id) -> str:
        """
        Url to set the cooling temperature setpoint
        """
        return Urls._ZONE_COOLING_SETPOINT_TEMPERATURE.format(serial_number='{serial_number}', zone_id=zone_id)

    @classmethod
    def zone_cooling_manual_setpoint_temperature(cls, zone_id) -> str:
        """
        Url to set manual cooling setpoint temperature
        """
        return Urls._ZONE_COOLING_MANUAL_SETPOINT_TEMPERATURE.format(serial_number='{serial_number}', zone_id=zone_id)
