import asyncio

from app_types.runable import Runable, SyncRunable


class CliApp(SyncRunable):
    """CLI приложение."""

    def __init__(self, origin_runable: Runable):
        """Конструктор класса.

        :param origin_runable: Runable
        """
        self._origin = origin_runable

    def run(self, args: list[str]):
        """Запуск.

        :param args: list[str]
        :return: int
        """
        asyncio.run(self._origin.run())
        return 0


class ForkCliApp(SyncRunable):
    """Маршрутизация для CLI приложения."""

    def __init__(self, *apps: SyncRunable):
        """Конструктор класса.

        :param apps: SyncRunable
        """
        self._apps = apps

    def run(self, args: list[str]):
        """Запуск.

        :param args: list[str]
        :return: int
        """
        for app in self._apps:
            app.run(args)
        return 0


class CommandCliApp(SyncRunable):
    """CLI команда."""

    def __init__(self, command: str, app: SyncRunable):
        """Конструктор класса.

        :param command: str
        :param app: SyncRunable
        """
        self._command = command
        self._app = app

    def run(self, args: list[str]) -> int:
        """Запуск.

        :param args: list[str]
        :return: int
        """
        if args[1] != self._command:
            return 1
        self._app.run(args)
        return 0
