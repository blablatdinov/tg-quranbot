class Runable(object):
    """Интерфейс запускаемого объекта."""

    async def run(self) -> None:
        """Запуск.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class SyncRunable(object):
    """Интерфейс блокирующего запускаемого объекта."""

    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError
