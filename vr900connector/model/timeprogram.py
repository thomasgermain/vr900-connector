"""Groups all time program related functionality. Time program is used when
*AUTO* operation mode is activated."""
import copy
from datetime import timedelta, datetime
from typing import List, Dict, Optional, Any

import re
import attr

from . import OperationMode


def _to_absolute_minutes(start_time: str) -> int:
    """Convert hh:mm to absolute minutes."""
    split = start_time.split(":")
    hour = int(split[0]) * 60
    minute = int(split[1])
    return hour + minute


# pylint: disable=too-few-public-methods
@attr.s
class TimeProgramDaySetting:
    """This class represents a time program setting within a day."""

    start_time = attr.ib(type=str)
    target_temperature = attr.ib(type=Optional[float])
    mode = attr.ib(type=Optional[OperationMode])
    absolute_minutes = attr.ib(type=int, init=False)

    def __attrs_post_init__(self) -> None:
        self.absolute_minutes = _to_absolute_minutes(self.start_time)

    # pylint: disable=unused-argument, no-self-use
    @start_time.validator
    def _validate_start_time(self, attribute: Any, value: Any) -> None:
        validator = re.compile('[0-9]{2}:[0-9]{2}')
        if not validator.match(value):
            raise ValueError(value)

    def __deepcopy__(self, memodict: Any = None) -> 'TimeProgramDaySetting':
        return TimeProgramDaySetting(self.start_time, self.target_temperature,
                                     self.mode)


# pylint: disable=too-few-public-methods
@attr.s
class TimeProgramDay:
    """This class represents a time program day, it's basically a list of
    TimeProgramDaySetting."""

    settings = attr.ib(type=List[TimeProgramDaySetting])


# pylint: disable=too-few-public-methods
@attr.s
class TimeProgram:
    """This class represents a time program (a week), reflecting the
    configuration done through mobile app."""

    days = attr.ib(type=Dict[str, TimeProgramDay])

    def get_for(self, search_date: datetime) -> TimeProgramDaySetting:
        """Return the corresponding time program day setting for a given date.
        """
        day = search_date.strftime("%A").lower()
        day_before = (search_date - timedelta(days=1)).strftime("%A").lower()
        time = str(search_date.hour) + ':' + str(search_date.minute)

        abs_minutes = _to_absolute_minutes(time)
        tp_day = self.days[day]
        tp_day_before = self.days[day_before]

        # if given hour:minute is before the first setting of the day,
        # get last setting of the previous day
        if abs_minutes < tp_day.settings[0].absolute_minutes:
            return copy.deepcopy(tp_day_before.settings[-1])

        idx: int = 0
        max_len: int = len(tp_day.settings)
        while idx < max_len and\
                abs_minutes > tp_day.settings[idx].absolute_minutes:
            idx += 1

        if not idx == max_len:
            # At this point, we went 1 step too far, so idx - 1
            return copy.deepcopy(tp_day.settings[idx - 1])

        # if no match a this point, it means search date is after the last
        # setting of the day
        return copy.deepcopy(tp_day.settings[-1])
