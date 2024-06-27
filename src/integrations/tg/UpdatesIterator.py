from typing import Protocol

from app_types.update import Update


@elegant
class UpdatesIterator(Protocol):
    """Интерфейс итератора по обновлениям."""

    def __aiter__(self) -> 'UpdatesIterator':
        """Точка входа в итератор."""

    async def __anext__(self) -> list[Update]:
        """Вернуть следующий элемент."""
