import copy
from datetime import timedelta, datetime
from typing import List, Dict
from . import HeatingMode


class TimeProgramDaySetting:
    """
    This class represents a time program setting within a day

    Args:
        start_time: Start time of the setting (format hh:mm)
        target_temperature: Target temperature of the setting
        mode: The mode that will be applied to the component (always None for a :class: `vr900connector.Room`)
    """
    def __init__(self, start_time: str, target_temperature: float, mode: HeatingMode):
        self.start_time = start_time
        self.target_temperature = target_temperature
        self.mode = mode
        self.absolute_minutes = TimeProgramDaySetting.to_absolute_minute(start_time)

    @classmethod
    def to_absolute_minute(cls, start_time) -> int:
        split = start_time.split(":")
        if len(split) > 1:
            hour = int(split[0]) * 60
            minute = int(split[1])
            return hour + minute
        raise ValueError(start_time)

    def __deepcopy__(self, memodict={}):
        return TimeProgramDaySetting(self.start_time, self.target_temperature, self.mode)


class TimeProgramDay:
    """
    This class represents a time program day, it's basically a list of :class: `vr900connector.TimeProgramDaySetting`

    Args:
        time_program_day_settings: list of settings (:class: `vr900connector.TimeProgramDaySetting`)
    """

    def __init__(self, time_program_day_settings: List[TimeProgramDaySetting]):
        self.time_program_day_settings = time_program_day_settings


class TimeProgram:
    """
    This class represents a time program (a week)

    Args:
        time_program_days: List of time program day (:class: `vr900connector.TimeProgramDay`)
    """

    def __init__(self, time_program_days: Dict[str, TimeProgramDay]):
        self.time_program_days = time_program_days

    def get_time_program_for(self, search_date: datetime) -> TimeProgramDaySetting:
        """
        This return the corresponding time program day setting for a given date

        :param search_date: The date for which you want to get the :class:`vr900connector.TimeProgramDaySetting`
        :return: The time program day setting corresponding to the date
        """
        day = search_date.strftime("%A").lower()
        day_before = (search_date - timedelta(days=1)).strftime("%A").lower()
        time = str(search_date.hour) + ':' + str(search_date.minute)

        absolute_minute = TimeProgramDaySetting.to_absolute_minute(time)
        timeProgramDay = self.time_program_days[day]
        timeProgramDayBefore = self.time_program_days[day_before]

        # if given hour:minute is before the first setting of the day, get last setting of the previous day
        if absolute_minute < timeProgramDay.time_program_day_settings[0].absolute_minutes:
            return copy.deepcopy(timeProgramDayBefore.time_program_day_settings[-1])
        else:
            idx = 0
            while idx < len(timeProgramDay.time_program_day_settings) - 1:
                if absolute_minute > timeProgramDay.time_program_day_settings[idx].absolute_minutes and \
                        (idx + 1 == len(timeProgramDay.time_program_day_settings)
                         or absolute_minute < timeProgramDay.time_program_day_settings[idx + 1].absolute_minutes):
                    return copy.deepcopy(timeProgramDay.time_program_day_settings[idx])
                idx += 1

            # if no match a this point, it means search date is after the last setting of the day
            return copy.deepcopy(timeProgramDay.time_program_day_settings[-1])
