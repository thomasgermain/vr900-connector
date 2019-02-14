from datetime import timedelta


class TimeProgramDaySetting:
    startTime = None
    temperature = None
    mode = None
    absoluteMinutes = None

    def __init__(self, start_time, temperature, mode):
        self.startTime = start_time
        self.temperature = temperature
        self.mode = mode
        self.absoluteMinutes = TimeProgramDaySetting.to_absolute_minute(start_time)

    @classmethod
    def to_absolute_minute(cls, start_time):
        split = start_time.split(":")
        if len(split) > 1:
            hour = int(split[0]) * 60
            minute = int(split[1])
            return hour + minute
        return 0


class TimeProgramDay:
    timeProgramDaySettings = []

    def add_setting(self, start_time, temperature, mode):
        self.timeProgramDaySettings.append(TimeProgramDaySetting(start_time, temperature, mode))


class TimeProgram:
    timeProgramDays = dict()

    def add_day(self, day, time_program_day):
        self.timeProgramDays[day] = time_program_day

    def get_current_time_program(self, search_date):
        day = search_date.strftime("%A").lower()
        day_before = (search_date - timedelta(days=1)).strftime("%A").lower()
        time = str(search_date.hour) + ":" + str(search_date.minute)

        absolute_minute = TimeProgramDaySetting.to_absolute_minute(time)
        timeProgramDay = self.timeProgramDays[day]
        timeProgramDayBefore = self.timeProgramDays[day_before]

        """if hour:minute is before the first setting of the day, check the last of day -1"""
        if absolute_minute < timeProgramDay.timeProgramDaySettings[0].absoluteMinutes:
            return timeProgramDayBefore.timeProgramDaySettings[-1]
        else:
            idx = 0
            while idx < len(timeProgramDay.timeProgramDaySettings) - 1:
                if absolute_minute > timeProgramDay.timeProgramDaySettings[idx].absoluteMinutes and \
                        (idx + 1 == len(timeProgramDay.timeProgramDaySettings)
                         or absolute_minute < timeProgramDay.timeProgramDaySettings[idx + 1].absoluteMinutes):
                    return timeProgramDay.timeProgramDaySettings[idx]
                idx += 1

            if idx == 0:
                return timeProgramDay.timeProgramDaySettings[0]
            elif idx == len(timeProgramDay.timeProgramDaySettings) - 1:
                return timeProgramDay.timeProgramDaySettings[-1]
        return None
