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
import json
from typing import final
from typing import Protocol

import httpx

from app_types.intable import Intable
from app_types.stringable import Stringable


class UpdatesTimeout(Intable):
    """Таймаут для обновлений."""

    def __int__(self):
        """Числовое представление.

        :return: int
        """
        return 5


class UpdatesURLInterface(Protocol):
    """Интерфейс URL запроса для получения уведомлений."""

    def generate(self, update_id: int) -> str:
        """Генерация.

        :param update_id: int
        """


class UpdatesURL(Stringable):
    """Базовый URL обновлений из телеграма."""

    def __init__(self, token: str):
        """Конструктор класса.

        :param token: str
        """
        self._token = token

    def __str__(self):
        """Строчное представление.

        :return: str
        """
        return 'https://api.telegram.org/bot{0}/getUpdates'.format(self._token)


class UpdatesWithOffsetURL(UpdatesURLInterface):
    """URL для получения только новых обновлений."""

    def __init__(self, updates_url: Stringable):
        """Конструктор класса.

        :param updates_url: Stringable
        """
        self._updates_url = updates_url

    def generate(self, update_id: int):
        """Генерация.

        :param update_id: int
        :return: str
        """
        return '{0}?offset={1}'.format(self._updates_url, update_id)


class UpdatesLongPollingURL(UpdatesURLInterface):
    """URL обновлений с таймаутом."""

    def __init__(self, updates_url: UpdatesURLInterface, long_polling_timeout: Intable):
        """Конструктор класса.

        :param updates_url: UpdatesURLInterface
        :param long_polling_timeout: Intable
        """
        self._origin = updates_url
        self._long_polling_timeout = long_polling_timeout

    def generate(self, update_id: int):
        """Генерация.

        :param update_id: int
        :return: str
        """
        return httpx.URL(self._origin.generate(update_id)).copy_add_param(
            'timeout',
            int(self._long_polling_timeout),
        )


class UpdatesIteratorInterface(Protocol):
    """Интерфейс итератора по обновлениям."""

    def __aiter__(self):
        """Точка входа в итератор."""

    async def __anext__(self) -> list[str]:
        """Вернуть следующий элемент."""


class PollingUpdatesIterator(UpdatesIteratorInterface):
    """Итератор по обновлениям."""

    def __init__(self, updates_url: UpdatesURLInterface, updates_timeout: Intable):
        """Конструктор класса.

        :param updates_url: UpdatesURLInterface
        :param updates_timeout: Intable
        """
        self._updates_url = updates_url
        self._offset = 0
        self._updates_timeout = updates_timeout

    def __aiter__(self):
        """Точка входа в итератор.

        :return: PollingUpdatesIterator
        """
        return self

    async def __anext__(self) -> list[str]:
        """Вернуть следующий элемент.

        :return: list[Update]
        """
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    self._updates_url.generate(self._offset),
                    timeout=int(self._updates_timeout),
                )
            except httpx.ReadTimeout:
                return []
            resp_content = resp.text
            try:
                parsed_result = json.loads(resp_content)['result']
            except KeyError:
                return []
            if not parsed_result:
                return []
            self._offset = parsed_result[-1]['update_id'] + 1
            return [json.dumps(elem, ensure_ascii=False) for elem in parsed_result]
