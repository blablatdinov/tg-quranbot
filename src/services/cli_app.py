import asyncio

from app_types.runable import Runable, SyncRunable


class CliApp(SyncRunable):

    def __init__(self, origin_runable: Runable):
        self._origin = origin_runable

    def run(self, args: list[str]):
        asyncio.run(self._origin.run())
        return 0


class ForkCliApp(SyncRunable):

    def __init__(self, *apps: SyncRunable):
        self._apps = apps

    def run(self, args: list[str]):
        for app in self._apps:
            app.run(args)


class CommandCliApp(SyncRunable):

    def __init__(self, command: str, app: SyncRunable):
        self._command = command
        self._app = app

    def run(self, args: list[str]) -> int:
        if args[1] != self._command:
            return 1
        self._app.run(args)
