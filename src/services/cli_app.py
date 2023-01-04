"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
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
