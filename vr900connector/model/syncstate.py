"""state module"""
from datetime import datetime

import attr

_PENDING = 'PENDING'
_SYNC = 'SYNCED'
_OUTDATED = 'OUTDATED'
_INITIALIZING = 'INITIALIZING'


@attr.s
class SyncState:
    """Sync state coming from the API."""

    state = attr.ib(type=str)
    timestamp = attr.ib(type=datetime)
    resource_link = attr.ib(type=str)

    @property
    def is_sync(self) -> bool:
        """Check if state is sync."""
        return self.state == _SYNC

    @property
    def is_pending(self) -> bool:
        """Check if state is pending."""
        return self.state == _PENDING

    @property
    def is_outdated(self) -> bool:
        """Check if state is outdated."""
        return self.state == _OUTDATED

    @property
    def is_init(self) -> bool:
        """Check if state is initializing."""
        return self.state == _INITIALIZING
