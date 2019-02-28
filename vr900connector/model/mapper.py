import datetime

from . import BoilerStatus, Circulation, Device, HolidayMode, HotWater, QuickMode, QuickVeto, Room, TimeProgram, \
    TimeProgramDay, TimeProgramDaySetting, Zone

_DATE_FORMAT = "%Y-%m-%d"


class Mapper:

    @staticmethod
    def quick_mode(full_system):
        quick_mode = full_system.get("body").get("configuration", dict()).get("quickmode")
        if quick_mode:
            return QuickMode.from_name(quick_mode.get("quickmode"))

    @staticmethod
    def outdoor_temp(full_system):
        return full_system.get("body").get("status", dict()).get('outside_temperature')

    @staticmethod
    def installation_name(facilities):
        return facilities.get("body", dict()).get("facilitiesList", list())[0].get("name")

    @staticmethod
    def rooms(raw_rooms):
        rooms = list()
        if raw_rooms:
            for raw_room in raw_rooms.get("body", dict()).get("rooms"):
                rooms.append(Mapper.room(raw_room))

        return rooms

    @staticmethod
    def room(raw_room):
        raw_room = raw_room.get("body") if raw_room.get("body") is not None else raw_room
        config = raw_room.get("configuration", dict())

        component_id = raw_room.get("roomIndex")
        child_lock = config.get("childLock")
        target_temp = config.get("temperatureSetpoint")
        current_temp = config.get("currentTemperature")
        devices = Mapper.devices(config.get("devices"))
        window_open = config.get("isWindowOpen")
        name = config.get("name")
        operation_mode = config.get("operationMode")

        raw_quickVeto = config.get("quickVeto")
        quick_veto = None
        if raw_quickVeto:
            quick_veto = QuickVeto(raw_quickVeto.get("remainingDuration"), config.get("temperatureSetpoint"))

        time_program = Mapper.time_program(raw_room.get("timeprogram"))

        return Room(component_id, name, time_program, current_temp, target_temp, operation_mode, quick_veto, child_lock,
                    window_open, devices)

    @staticmethod
    def devices(raw_devices):
        devices = list()
        if raw_devices:
            for raw_device in raw_devices:
                name = raw_device["name"]
                device_type = raw_device["deviceType"]
                battery_low = raw_device["isBatteryLow"]
                radio_out_of_reach = raw_device["isRadioOutOfReach"]
                sgtin = raw_device["sgtin"]
                devices.append(Device(name, sgtin, device_type, battery_low, radio_out_of_reach))

        return devices

    @staticmethod
    def time_program(raw_time_program, mode_key_name=""):
        result = dict()
        if raw_time_program:
            result["monday"] = Mapper.time_program_day(raw_time_program.get("monday"), mode_key_name)
            result["tuesday"] = Mapper.time_program_day(raw_time_program.get("tuesday"), mode_key_name)
            result["wednesday"] = Mapper.time_program_day(raw_time_program.get("wednesday"), mode_key_name)
            result["thursday"] = Mapper.time_program_day(raw_time_program.get("thursday"), mode_key_name)
            result["friday"] = Mapper.time_program_day(raw_time_program.get("friday"), mode_key_name)
            result["saturday"] = Mapper.time_program_day(raw_time_program.get("saturday"), mode_key_name)
            result["sunday"] = Mapper.time_program_day(raw_time_program.get("sunday"), mode_key_name)

        return TimeProgram(result)

    @staticmethod
    def time_program_day(raw_time_program_day, mode_key_name=""):
        time_program_day_settings = list()
        if raw_time_program_day:
            for time_setting in raw_time_program_day:
                start_time = time_setting.get("startTime")
                target_temp = time_setting.get("temperatureSetpoint")
                mode = time_setting.get(mode_key_name)
                time_program_day_settings.append(TimeProgramDaySetting(start_time, target_temp, mode))

        return TimeProgramDay(time_program_day_settings)

    @staticmethod
    def holiday_mode(full_system):
        holidayMode = HolidayMode(False, None, None, None)

        raw_holiday_mode = full_system.get("body", dict()).get("configuration", dict()).get("holidaymode")
        if raw_holiday_mode and raw_holiday_mode.get("active"):
            holidayMode.active = True
            holidayMode.targetTemperature = raw_holiday_mode.get("temperature_setpoint")
            holidayMode.startDate = datetime.datetime.strptime(raw_holiday_mode.get("start_date"), _DATE_FORMAT).date()
            holidayMode.endDate = datetime.datetime.strptime(raw_holiday_mode.get("end_date"), _DATE_FORMAT).date()

        return holidayMode

    @staticmethod
    def boiler_status(hvac_state):
        hvac_state_info = Mapper.__find_hvac_message_status(hvac_state)
        if hvac_state_info:
            timestamp = hvac_state_info.get("timestamp")
            last_update = None
            if timestamp:
                last_update = datetime.datetime.fromtimestamp(timestamp / 1000)

            device_name = hvac_state_info.get("deviceName")
            code = hvac_state_info.get("statusCode")
            title = hvac_state_info.get("title")
            description = hvac_state_info.get("description")
            hint = hvac_state_info.get("hint")

            return BoilerStatus(device_name, description, title, code, hint, last_update)

    @staticmethod
    def zones(full_system):
        zones = list()
        for raw_zone in full_system.get("body", dict()).get("zones", list()):
            zones.append(Mapper.zone(raw_zone))

        return zones

    @staticmethod
    def zone(raw_zone):
        # meta = meta if meta is not None else raw_zone.get("meta", dict())

        heating = raw_zone.get("heating", dict())
        configuration = raw_zone.get("configuration", dict())
        heating_configuration = heating.get("configuration", dict())

        zone_id = raw_zone.get("_id")
        operation_mode = heating_configuration.get("mode")
        target_temp = heating_configuration.get("setpoint_temperature")
        target_min_temp = heating_configuration.get("setback_temperature")
        time_program = Mapper.time_program(heating.get("timeprogram"), "setting")

        name = configuration.get("name").strip()
        current_temperature = configuration.get("inside_temperature")
        active_function = configuration.get("active_function")

        raw_quick_veto = configuration.get("quick_veto")
        quick_veto = None
        if raw_quick_veto and raw_quick_veto.get("active"):
            # No way to find start_date Quick veto on zone lasts 6 hours
            quick_veto = QuickVeto(-1, raw_quick_veto.get("setpoint_temperature"))

        rbr = raw_zone.get("currently_controlled_by", dict()).get("name", "") == "RBR"

        return Zone(zone_id, name, time_program, current_temperature, target_temp, operation_mode, quick_veto,
                    target_min_temp, active_function, rbr)

    @staticmethod
    def domestic_hot_water(full_system, live_report):
        hot_water_list = full_system.get("body", dict()).get("dhw", list())

        if hot_water_list:
            raw_hot_water = hot_water_list[0].get("hotwater")
            if raw_hot_water:
                target_temp = raw_hot_water.get("configuration", dict()).get("temperature_setpoint")
                operation_mode = raw_hot_water.get("configuration", dict()).get("operation_mode")
                time_program = Mapper.time_program(raw_hot_water.get("timeprogram", dict()), "mode")
                dwh_id = hot_water_list[0].get("_id")
                dhw_report = Mapper.__find_dhw_temperature_report(live_report)

                current_temp = None
                name = None
                if dhw_report:
                    current_temp = dhw_report.get("value")
                    name = dhw_report.get("name")

                return HotWater(dwh_id, name, time_program, current_temp, target_temp, operation_mode)

    @staticmethod
    def circulation(full_system):
        hot_water_list = full_system.get("body", dict()).get("dhw", list())

        if hot_water_list:
            raw_circulation = hot_water_list[0].get("circulation")
            if raw_circulation:
                name = "Circulation"
                time_program = Mapper.time_program(raw_circulation.get("timeprogram", "setting"))
                operation_mode = raw_circulation.get("configuration", dict()).get("operationMode")
                dhw_id = hot_water_list[0].get("_id")

                return Circulation(dhw_id, name, time_program, operation_mode)

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

    @staticmethod
    def __find_zone_quick_veto_timestamp(zone_id, meta):
        for state in meta.get("resourceState", list()):
            if state.get("link", dict()).get("resourceLink", "") \
                    .find("/zones/" + zone_id + "/configuration/quick_veto"):
                return state.get("timestamp")
        return None

    @staticmethod
    def __find_dhw_quick_veto_timestamp(meta):
        for state in meta.get("resourceState", list()):
            if state.get("link", dict()).get("resourceLink", "") \
                    .find("/systemcontrol/v1/configuration/quickmode"):
                return state.get("timestamp")
        return None

    @staticmethod
    def __get_delta(start_time, time_to_add):
        end_time = start_time + time_to_add
        delta = (end_time / 1000) - datetime.datetime.now().timestamp()
        return int(delta / 60)
