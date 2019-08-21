"""Grouping status"""
from datetime import datetime
from typing import Optional

import attr


# pylint: disable=too-few-public-methods
@attr.s
class BoilerStatus:
    """Status + some information about the boiler."""

    device_name = attr.ib(type=str)
    description = attr.ib(type=str)
    title = attr.ib(type=str)
    code = attr.ib(type=Optional[str])
    hint = attr.ib(type=str)
    last_update = attr.ib(type=Optional[datetime])
    water_pressure = attr.ib(type=Optional[float])
    current_temperature = attr.ib(type=Optional[float])

    @property
    def is_error(self) -> bool:
        """Checks if there is an error at boiler side."""
        return self.code is not None \
            and (self.code.startswith('F') or self.code == 'con')


@attr.s
class SystemStatus:
    """Status of the system."""

    online_status = attr.ib(type=str)
    update_status = attr.ib(type=str)

    @property
    def is_online(self) -> bool:
        """Checks if the system is connected to the internet."""
        return self.online_status == 'ONLINE'

    @property
    def is_up_to_date(self) -> bool:
        """Checks if the system is up to date."""
        return self.update_status == 'UPDATE_NOT_PENDING'
