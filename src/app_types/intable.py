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
from typing import Protocol


class Intable(Protocol):
    """Интерфейс объектов, которые можно привести к числу."""

    def __int__(self) -> int:
        """Приведение к числу."""


class AsyncIntable(Protocol):
    """Интерфейс объектов, которые можно привести к числу."""

    async def to_int(self) -> int:
        """Приведение к числу с возможностью переключения контекста."""


class ThroughIntable(Intable):
    """Сквозное число."""

    def __init__(self, source: int):
        """Конструктор класса.

        :param source: int
        """
        self._source = source

    def __int__(self) -> int:
        """Приведение к числу.

        :return: int
        """
        return self._source


class ThroughAsyncIntable(AsyncIntable):
    """Сквозное число."""

    def __init__(self, source: int):
        """Конструктор класса.

        :param source: int
        """
        self._source = source

    async def to_int(self) -> int:
        """Приведение к числу с возможностью переключения контекста.

        :return: int
        """
        return self._source


class SyncToAsyncIntable(AsyncIntable):
    """Объект для использования синхронного Intable в кач-ве асинхронного AsyncIntable."""

    def __init__(self, origin: Intable):
        """Конструктор класса.

        :param origin: Intable
        """
        self._origin = origin

    async def to_int(self) -> int:
        """Числовое представление.

        :return: int
        """
        return int(self._origin)
