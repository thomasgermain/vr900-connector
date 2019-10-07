"""Errors coming from vaillant API."""
from datetime import datetime
import attr


# pylint: disable=too-few-public-methods
@attr.s
class Error:
    """Errors coming from your system.

    Args:
        device_name (str): Name of the device from where the error is coming.
        title (str): Short description of the error.
        status_code (str): Code of the error.
        description (str): Long description of the error.
        timestamp (datetime): When errors occurred.
    """

    device_name = attr.ib(type=str)
    title = attr.ib(type=str)
    status_code = attr.ib(type=str)
    description = attr.ib(type=str)
    timestamp = attr.ib(type=datetime)
