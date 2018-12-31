import datetime

from model import Room, Device, TimeProgram, TimeProgramDay, HolidayMode, BoilerStatus, DomesticHotWater, Circulation, \
    BoxDetails, Zone, QuickVeto

DATE_FORMAT = "%Y-%m-%d"


class Mapper:

    @staticmethod
    def rooms(raw_rooms):
        rooms = list()
        if raw_rooms is not None:
            for raw_room in raw_rooms.get("body", dict()).get("rooms"):
                rooms.append(Mapper.room(raw_room))

        return rooms

    @staticmethod
    def room(raw_room):
        room = Room()
        raw_room = raw_room.get("body") if raw_room.get("body") is not None else raw_room
        config = raw_room.get("configuration", dict())

        room.id = raw_room.get("roomIndex")
        room.childLock = config.get("childLock")
        room.configuredTemperature = config.get("temperatureSetpoint")
        room.currentTemperature = config.get("currentTemperature")
        room.devices = Mapper.devices(config.get("devices"))
        room.isWindowOpen = config.get("isWindowOpen")
        room.name = config.get("name")
        room.operationMode = config.get("operationMode")

        raw_quickVeto = config.get("quickVeto")
        if raw_quickVeto:
            room.quickVeto = QuickVeto(raw_quickVeto.get("remainingDuration"), config.get("temperatureSetpoint"))

        room.timeProgram = Mapper.time_program(raw_room.get("timeprogram"))
        return room

    @staticmethod
    def devices(raw_devices):
        devices = list()
        if raw_devices is not None:
            for raw_device in raw_devices:
                device = Device()
                device.name = raw_device["name"]
                device.deviceType = raw_device["deviceType"]
                device.isBatteryLow = raw_device["isBatteryLow"]
                device.isRadioOutOfReach = raw_device["isRadioOutOfReach"]
                device.sgtin = raw_device["sgtin"]
                devices.append(device)

        return devices

    @staticmethod
    def time_program(raw_time_program, mode_key_name=""):
        timeProgram = TimeProgram()
        if raw_time_program is not None:
            timeProgram.add_day("monday", Mapper.time_program_day(raw_time_program.get("monday"), mode_key_name))
            timeProgram.add_day("tuesday", Mapper.time_program_day(raw_time_program.get("tuesday"), mode_key_name))
            timeProgram.add_day("wednesday", Mapper.time_program_day(raw_time_program.get("wednesday"), mode_key_name))
            timeProgram.add_day("thursday", Mapper.time_program_day(raw_time_program.get("thursday"), mode_key_name))
            timeProgram.add_day("friday", Mapper.time_program_day(raw_time_program.get("friday"), mode_key_name))
            timeProgram.add_day("saturday", Mapper.time_program_day(raw_time_program.get("saturday"), mode_key_name))
            timeProgram.add_day("sunday", Mapper.time_program_day(raw_time_program.get("sunday"), mode_key_name))

        return timeProgram

    @staticmethod
    def time_program_day(raw_time_program_day, mode_key_name=""):
        timeProgramDay: TimeProgramDay = TimeProgramDay()
        if raw_time_program_day is not None:
            for time_setting in raw_time_program_day:
                timeProgramDay.add_setting(time_setting.get("startTime"), time_setting.get("temperatureSetpoint"),
                                           time_setting.get(mode_key_name))

        return timeProgramDay

    @staticmethod
    def holiday_mode(full_system):
        holidayMode = None
        raw_holiday_mode = full_system.get("body", dict()).get("configuration", dict()).get("holidaymode")
        if raw_holiday_mode is not None:
            holidayMode = HolidayMode()
            holidayMode.configuredTemperature = raw_holiday_mode.get("temperature_setpoint")
            holidayMode.active = raw_holiday_mode.get("active")
            holidayMode.startDate = datetime.datetime.strptime(raw_holiday_mode.get("start_date"), DATE_FORMAT)
            holidayMode.endDate = datetime.datetime.strptime(raw_holiday_mode.get("end_date"), DATE_FORMAT)

        return holidayMode

    @staticmethod
    def boiler_status(hvac_state, live_report):
        boilerStatus = BoilerStatus()

        hvac_state_info = Mapper.__find_hvac_message_status(hvac_state)
        if hvac_state_info is not None:
            timestamp = hvac_state_info.get("timestamp")
            if timestamp is not None:
                boilerStatus.lastUpdate = datetime.datetime.fromtimestamp(timestamp / 1000)

            boilerStatus.deviceName = hvac_state_info.get("deviceName")
            boilerStatus.code = hvac_state_info.get("statusCode")
            boilerStatus.title = hvac_state_info.get("title")
            boilerStatus.description = hvac_state_info.get("description")
            boilerStatus.hint = hvac_state_info.get("hint")

        water_pressure_report = Mapper.__find_water_pressure_report(live_report)
        if water_pressure_report is not None:
            boilerStatus.waterPressure = water_pressure_report.get("value")
            boilerStatus.waterPressureUnit = water_pressure_report.get("unit")

        boiler_temp_report = Mapper.__find_boiler_temperature_report(live_report)
        if boiler_temp_report is not None:
            boilerStatus.currentTemperature = boiler_temp_report.get("value")

        return boilerStatus

    @staticmethod
    def box_detail(facilities, system_status):
        boxDetails = None

        facilityList = facilities.get("body", dict()).get("facilitiesList", list())

        if facilityList:
            boxDetails = BoxDetails()

            details = facilityList[0]
            boxDetails.serialNumber = details.get("serialNumber")
            boxDetails.firmwareVersion = details.get("firmwareVersion")

            network = details.get("networkInformation", dict())
            boxDetails.ethernetMac = network.get("macAddressEthernet")
            boxDetails.wifiMac = network.get("macAddressWifiClient")
            boxDetails.wifiAPMac = network.get("macAddressWifiAccessPoint")

            boxDetails.onlineStatus = system_status.get("body", dict()).get("onlineStatus", dict()).get("status")
            boxDetails.updateStatus = system_status.get("body", dict()).get("firmwareUpdateStatus", dict()).get("status")

        return boxDetails

    @staticmethod
    def zones(full_system):
        zones = list()
        meta = full_system.get("meta", dict()).get("resourceState", list())
        for raw_zone in full_system.get("body", dict()).get("zones", list()):
            zones.append(Mapper.zone(raw_zone, meta))

        return zones

    @staticmethod
    def zone(raw_zone, meta=None):
        zone = Zone()

        meta = meta if meta is not None else raw_zone.get("meta", dict())
        zone.id = raw_zone.get("_id")

        heating = raw_zone.get("heating", dict())
        zone.operationMode = heating.get("configuration", dict()).get("mode")
        zone.configuredTemperature = heating.get("configuration", dict()).get("setpoint_temperature")
        zone.configuredMinTemperature = heating.get("configuration", dict()).get("setback_temperature")
        zone.timeProgram = Mapper.time_program(heating.get("timeprogram"), "setting")

        configuration = raw_zone.get("configuration", dict())
        zone.name = configuration.get("name").strip()
        zone.currentTemperature = configuration.get("inside_temperature")
        zone.activeFunction = configuration.get("active_function")

        quickVeto = configuration.get("quick_veto")
        if quickVeto and quickVeto.get("active"):
            timestamp = Mapper.__find_zone_quick_veto_timestamp(zone.id, meta)

            if timestamp:
                """timestamp is the start date of the quick veto. Quick veto on zone lasts 6 hours"""
                end_timestamp = timestamp + 6 * 60 * 60 * 1000
                end_timestamp /= 1000
                remaining = end_timestamp - datetime.datetime.now().timestamp()
                remaining = int(remaining/60)
                zone.quickVeto = QuickVeto(remaining, quickVeto.get("setpoint_temperature"),
                                           datetime.datetime.fromtimestamp(timestamp/1000))

        zone.rbr = raw_zone.get("currently_controlled_by", dict()).get("name", "") == "RBR"

        return zone

    @staticmethod
    def __find_zone_quick_veto_timestamp(zone_id, meta):
        for state in meta:
            if state.get("link", dict()).get("resourceLink", "")\
                    .find("/zones/" + zone_id + "/configuration/quick_veto"):
                return state.get("timestamp")
        return None

    @staticmethod
    def domestic_hot_water(full_system, live_report):
        domesticHotWater = None
        dhws = full_system.get("body", dict()).get("dhw", list())

        if dhws:
            dhw = dhws[0].get("hotwater")
            if dhw is not None:
                domesticHotWater = DomesticHotWater()
                domesticHotWater.configuredTemperature = dhw.get("configuration", dict()).get("temperature_setpoint")
                domesticHotWater.operationMode = dhw.get("configuration", dict()).get("operation_mode")
                domesticHotWater.timeProgram = Mapper.time_program(dhw.get("timeprogram", "mode"))
                domesticHotWater.id = dhws[0].get("_id")

            dhw_report = Mapper.__find_dhw_temperature_report(live_report)

            if dhw_report is not None:
                domesticHotWater.currentTemperature = dhw_report.get("value")
                domesticHotWater.name = dhw_report.get("name")

        return domesticHotWater

    @staticmethod
    def circulation(full_system):
        circulation = None
        dhws = full_system.get("body", dict()).get("dhw", list())

        if dhws:
            raw_circulation = dhws[0].get("circulation")
            if raw_circulation is not None:
                circulation = Circulation()
                circulation.name = "Circulation"
                circulation.timeProgram = Mapper.time_program(raw_circulation.get("timeprogram", "setting"))
                circulation.operationMode = raw_circulation.get("configuration", dict()).get("operationMode")
                circulation.id = dhws[0].get("_id")

        return circulation

    @staticmethod
    def __find_hvac_message_status(hvac_state):
        for message in hvac_state.get("body", dict()).get("errorMessages"):
            if message.get("type") == "STATUS":
                return message

        return None

    @staticmethod
    def __find_water_pressure_report(live_report):
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "HEATING" and report.get("_id") == "WaterPressureSensor":
                    return report

        return None

    @staticmethod
    def __find_boiler_temperature_report(live_report):
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "HEATING" \
                        and report.get("_id") == "FlowTemperatureSensor":
                    return report

        return None

    @staticmethod
    def __find_dhw_temperature_report(live_report):
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "DHW" \
                        and report.get("_id") == "DomesticHotWaterTankTemperature":
                    return report

        return None
