from typing import Protocol

from app_types.update import Update


@elegant
class DebugParam(Protocol):
    """Интерфейс отладочной информации."""

    async def debug_value(self, update: Update) -> str:
        """Значение отладочной информации.

        :param update: Update
        """
