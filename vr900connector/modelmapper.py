import datetime

from model import Room, Device, TimeProgram, TimeProgramDay, HolidayMode, BoilerStatus, DomesticHotWater, Circulation, \
    BoxDetails, Zone, QuickMode, QuickVeto

DATE_FORMAT = "%Y-%m-%d"


class Mapper:

    def quick_mode(self, full_system):
        quick_mode = full_system.get("body").get("configuration", dict()).get("quickmode")
        if quick_mode:
            return QuickMode(quick_mode.get("quickmode"), quick_mode.get("duration"))

    def outside_temp(self, full_system):
        return full_system.get("body").get("status", dict()).get('outside_temperature')

    def installation_name(self, facilities):
        return facilities.get("body", dict()).get("facilitiesList", list())[0].get("name")

    def rooms(self, raw_rooms):
        rooms = list()
        if raw_rooms is not None:
            for raw_room in raw_rooms.get("body", dict()).get("rooms"):
                rooms.append(self.room(raw_room))

        return rooms

    def room(self, raw_room):
        room = Room()
        raw_room = raw_room.get("body") if raw_room.get("body") is not None else raw_room
        config = raw_room.get("configuration", dict())

        room.id = raw_room.get("roomIndex")
        room.childLock = config.get("childLock")
        room.configuredTemperature = config.get("temperatureSetpoint")
        room.currentTemperature = config.get("currentTemperature")
        room.devices = self.devices(config.get("devices"))
        room.isWindowOpen = config.get("isWindowOpen")
        room.name = config.get("name")
        room.operationMode = config.get("operationMode")

        raw_quickVeto = config.get("quickVeto")
        if raw_quickVeto:
            room.quickVeto = QuickVeto(raw_quickVeto.get("remainingDuration"), config.get("temperatureSetpoint"))

        room.timeProgram = self.time_program(raw_room.get("timeprogram"))
        return room

    def devices(self, raw_devices):
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

    def time_program(self, raw_time_program, mode_key_name=""):
        timeProgram = TimeProgram()
        if raw_time_program is not None:
            timeProgram.add_day("monday", self.time_program_day(raw_time_program.get("monday"), mode_key_name))
            timeProgram.add_day("tuesday", self.time_program_day(raw_time_program.get("tuesday"), mode_key_name))
            timeProgram.add_day("wednesday", self.time_program_day(raw_time_program.get("wednesday"), mode_key_name))
            timeProgram.add_day("thursday", self.time_program_day(raw_time_program.get("thursday"), mode_key_name))
            timeProgram.add_day("friday", self.time_program_day(raw_time_program.get("friday"), mode_key_name))
            timeProgram.add_day("saturday", self.time_program_day(raw_time_program.get("saturday"), mode_key_name))
            timeProgram.add_day("sunday", self.time_program_day(raw_time_program.get("sunday"), mode_key_name))

        return timeProgram

    def time_program_day(self, raw_time_program_day, mode_key_name=""):
        timeProgramDay: TimeProgramDay = TimeProgramDay()
        if raw_time_program_day is not None:
            for time_setting in raw_time_program_day:
                timeProgramDay.add_setting(time_setting.get("startTime"), time_setting.get("temperatureSetpoint"),
                                           time_setting.get(mode_key_name))

        return timeProgramDay

    def holiday_mode(self, full_system):
        holidayMode = None
        raw_holiday_mode = full_system.get("body", dict()).get("configuration", dict()).get("holidaymode")
        if raw_holiday_mode is not None:
            holidayMode = HolidayMode()
            holidayMode.configuredTemperature = raw_holiday_mode.get("temperature_setpoint")
            holidayMode.active = raw_holiday_mode.get("active")
            holidayMode.startDate = datetime.datetime.strptime(raw_holiday_mode.get("start_date"), DATE_FORMAT)
            holidayMode.endDate = datetime.datetime.strptime(raw_holiday_mode.get("end_date"), DATE_FORMAT)

        return holidayMode

    def boiler_status(self, hvac_state, live_report):
        boilerStatus = BoilerStatus()

        hvac_state_info = self.__find_hvac_message_status(hvac_state)
        if hvac_state_info is not None:
            timestamp = hvac_state_info.get("timestamp")
            if timestamp is not None:
                boilerStatus.lastUpdate = datetime.datetime.fromtimestamp(timestamp / 1000)

            boilerStatus.deviceName = hvac_state_info.get("deviceName")
            boilerStatus.code = hvac_state_info.get("statusCode")
            boilerStatus.title = hvac_state_info.get("title")
            boilerStatus.description = hvac_state_info.get("description")
            boilerStatus.hint = hvac_state_info.get("hint")

        water_pressure_report = self.__find_water_pressure_report(live_report)
        if water_pressure_report is not None:
            boilerStatus.waterPressure = water_pressure_report.get("value")
            boilerStatus.waterPressureUnit = water_pressure_report.get("unit")

        boiler_temp_report = self.__find_boiler_temperature_report(live_report)
        if boiler_temp_report is not None:
            boilerStatus.currentTemperature = boiler_temp_report.get("value")

        return boilerStatus

    def box_detail(self, facilities, system_status):
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

    def zones(self, full_system):
        zones = list()
        meta = full_system.get("meta", dict())
        for raw_zone in full_system.get("body", dict()).get("zones", list()):
            zones.append(self.zone(raw_zone, meta))

        return zones

    def zone(self, raw_zone, meta=None):
        zone = Zone()

        # meta = meta if meta is not None else raw_zone.get("meta", dict())
        zone.id = raw_zone.get("_id")

        heating = raw_zone.get("heating", dict())
        configuration = raw_zone.get("configuration", dict())
        heating_configuration = heating.get("configuration", dict())
        zone.operationMode = heating_configuration.get("mode")
        zone.configuredTemperature = heating_configuration.get("setpoint_temperature")
        zone.configuredMinTemperature = heating_configuration.get("setback_temperature")
        zone.timeProgram = self.time_program(heating.get("timeprogram"), "setting")

        zone.name = configuration.get("name").strip()
        zone.currentTemperature = configuration.get("inside_temperature")
        zone.activeFunction = configuration.get("active_function")

        quickVeto = configuration.get("quick_veto")
        if quickVeto and quickVeto.get("active"):
            """No way to find start_date Quick veto on zone lasts 6 hours"""
            zone.quickVeto = QuickVeto(-1, quickVeto.get("setpoint_temperature"))

        zone.rbr = raw_zone.get("currently_controlled_by", dict()).get("name", "") == "RBR"

        return zone

    def domestic_hot_water(self, full_system, live_report):
        domesticHotWater = None
        dhws = full_system.get("body", dict()).get("dhw", list())

        if dhws:
            dhw = dhws[0].get("hotwater")
            if dhw is not None:
                domesticHotWater = DomesticHotWater()
                domesticHotWater.configuredTemperature = dhw.get("configuration", dict()).get("temperature_setpoint")
                domesticHotWater.operationMode = dhw.get("configuration", dict()).get("operation_mode")
                domesticHotWater.timeProgram = self.time_program(dhw.get("timeprogram", "mode"))
                domesticHotWater.id = dhws[0].get("_id")
                if dhws[0].get("controlled_by"):
                    """Didn't find a way to get start_date, and remaining = 0. Quick veto dhw is 1 hour"""
                    domesticHotWater.quickVeto = QuickVeto(-1, domesticHotWater.configuredTemperature)

            dhw_report = self.__find_dhw_temperature_report(live_report)

            if dhw_report is not None:
                domesticHotWater.currentTemperature = dhw_report.get("value")
                domesticHotWater.name = dhw_report.get("name")

        return domesticHotWater

    def circulation(self, full_system):
        circulation = None
        dhws = full_system.get("body", dict()).get("dhw", list())

        if dhws:
            raw_circulation = dhws[0].get("circulation")
            if raw_circulation is not None:
                circulation = Circulation()
                circulation.name = "Circulation"
                circulation.timeProgram = self.time_program(raw_circulation.get("timeprogram", "setting"))
                circulation.operationMode = raw_circulation.get("configuration", dict()).get("operationMode")
                circulation.id = dhws[0].get("_id")

        return circulation

    def __find_hvac_message_status(self, hvac_state):
        for message in hvac_state.get("body", dict()).get("errorMessages"):
            if message.get("type") == "STATUS":
                return message

        return None

    def __find_water_pressure_report(self, live_report):
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "HEATING" and report.get("_id") == "WaterPressureSensor":
                    return report

        return None

    def __find_boiler_temperature_report(self, live_report):
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "HEATING" \
                        and report.get("_id") == "FlowTemperatureSensor":
                    return report

        return None

    def __find_dhw_temperature_report(self, live_report):
        for device in live_report.get("body", dict()).get("devices", list()):
            for report in device.get("reports", list()):
                if report.get("associated_device_function") == "DHW" \
                        and report.get("_id") == "DomesticHotWaterTankTemperature":
                    return report

        return None

    def __find_zone_quick_veto_timestamp(self, zone_id, meta):
        for state in meta.get("resourceState", list()):
            if state.get("link", dict()).get("resourceLink", "") \
                    .find("/zones/" + zone_id + "/configuration/quick_veto"):
                return state.get("timestamp")
        return None

    def __find_dhw_quick_veto_timestamp(self, meta):
        for state in meta.get("resourceState", list()):
            if state.get("link", dict()).get("resourceLink", "") \
                    .find("/systemcontrol/v1/configuration/quickmode"):
                return state.get("timestamp")
        return None

    def __get_delta(self, start_time, time_to_add):
        end_time = start_time + time_to_add
        delta = (end_time / 1000) - datetime.datetime.now().timestamp()
        return int(delta / 60)
