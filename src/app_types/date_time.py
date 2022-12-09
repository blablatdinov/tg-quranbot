import datetime
from typing import Protocol


class DateTimeIterface(Protocol):
    """Интерфейс даты/времени."""

    def datetime(self) -> datetime.datetime:
        """Дата/время."""
