from model import Room, Device, TimeProgram, TimeProgramDay, HolidayMode


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

        room.index = raw_room.get("roomIndex")
        room.childLock = config.get("childLock")
        room.configuredTemperature = config.get("temperatureSetpoint")
        room.currentTemperature = config.get("currentTemperature")
        room.devices = Mapper.devices(config.get("devices"))
        room.icon = config.get("iconId")
        room.isWindowOpen = config.get("isWindowOpen")
        room.name = config.get("name")
        room.operationMode = config.get("operationMode")
        room.remainingQuickVeto = config.get("quickVeto", dict()).get("remainingDuration")
        room.timeProgram = raw_room.get("timeprogram")
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
    def time_program(raw_time_program):
        timeProgram = TimeProgram()
        if raw_time_program is not None:
            timeProgram.add_day("monday", Mapper.time_program_day(raw_time_program.get("monday")))
            timeProgram.add_day("tuesday", Mapper.time_program_day(raw_time_program.get("tuesday")))
            timeProgram.add_day("wednesday", Mapper.time_program_day(raw_time_program.get("wednesday")))
            timeProgram.add_day("thursday", Mapper.time_program_day(raw_time_program.get("thursday")))
            timeProgram.add_day("friday", Mapper.time_program_day(raw_time_program.get("friday")))
            timeProgram.add_day("saturday", Mapper.time_program_day(raw_time_program.get("saturday")))
            timeProgram.add_day("sunday", Mapper.time_program_day(raw_time_program.get("sunday")))

    @staticmethod
    def time_program_day(raw_time_program_day):
        timeProgramDay: TimeProgramDay = TimeProgramDay()
        if raw_time_program_day is not None:
            for time_setting in raw_time_program_day:
                timeProgramDay.add_setting(time_setting.get("startTime"), time_setting.get("temperatureSetpoint"))

        return timeProgramDay

    @staticmethod
    def holiday_mode(holidaymode):
        return HolidayMode

    @staticmethod
    def boiler_status(hvac_state, livereport):
        pass

    @staticmethod
    def box_status(system_status):
        pass

    @staticmethod
    def box_detail(facilities):
        pass

    @staticmethod
    def zones(zones):
        pass

    @staticmethod
    def domestic_hot_water(fullSystem, livereport):
        pass

    @staticmethod
    def circulation(full_system):
        pass
