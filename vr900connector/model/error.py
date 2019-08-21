"""Errors coming from vaillant API."""
from datetime import datetime
import attr


# pylint: disable=too-few-public-methods
@attr.s
class Error:
    """Errors coming from vaillant API."""

    device_name = attr.ib(type=str)
    title = attr.ib(type=str)
    status_code = attr.ib(type=str)
    description = attr.ib(type=str)
    timestamp = attr.ib(type=datetime)
