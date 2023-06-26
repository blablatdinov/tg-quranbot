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
from typing import Protocol, final

import attrs
from databases import Database

from exceptions.base_exception import InternalBotError


class RandomPodcastInterface(Protocol):
    """Интерфейс подкаста.

    https://www.yegor256.com/2014/12/01/orm-offensive-anti-pattern.html
    """

    async def audio_telegram_id(self) -> str:
        """Получить идентификатор файла."""

    async def link_to_audio_file(self) -> str:
        """Получить ссылку на файл."""


@final
@attrs.define(frozen=True)
class RandomPodcast(RandomPodcastInterface):
    """Объект подкаста."""

    _connection: Database

    async def audio_telegram_id(self) -> str:
        """Получить идентификатор файла.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        """
        query = """
            SELECT
                f.telegram_file_id
            FROM podcasts p
            INNER JOIN files f ON p.file_id = f.file_id
            ORDER BY RANDOM()
            LIMIT 1
        """
        row = await self._connection.fetch_one(query)
        if not row:
            raise InternalBotError('Подкасты не найдены')
        return row._mapping['telegram_file_id']  # noqa: WPS437

    async def link_to_audio_file(self) -> str:
        """Получить ссылку на файл.

        :returns: str
        :raises InternalBotError: если таблилца с подкастами не заполнена
        """
        query = """
            SELECT
                f.link
            FROM podcasts p
            INNER JOIN files f ON p.file_id = f.file_id
            ORDER BY RANDOM()
            LIMIT 1
        """
        row = await self._connection.fetch_one(query)
        if not row:
            raise InternalBotError('Подкасты не найдены')
        return row._mapping['link']  # noqa: WPS437
