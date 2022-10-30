from typing import Protocol


class Runable(Protocol):
    """Интерфейс запускаемого объекта."""

    async def run(self) -> None:
        """Запуск."""


class SyncRunable(Protocol):
    """Интерфейс блокирующего запускаемого объекта."""

    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        """
