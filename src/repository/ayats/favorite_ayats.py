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
from loguru import logger
from pyeo import elegant


@elegant
class FavoriteAyatRepositoryInterface(Protocol):
    """Интерфейс для работы с хранилищем избранных аятов."""

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Проверить входит ли аят в избранные.

        :param ayat_id: int
        :param chat_id: int
        """


@final
@attrs.define(frozen=True)
@elegant
class FavoriteAyatsRepository(FavoriteAyatRepositoryInterface):
    """Класс для работы с хранилищем избранных аятов."""

    _connection: Database

    async def check_ayat_is_favorite_for_user(self, ayat_id: int, chat_id: int) -> bool:
        """Получить аят по номеру суры.

        :param ayat_id: int
        :param chat_id: int
        :returns: bool
        """
        logger.debug('Check ayat <{0}> is favorite for user <{1}>...'.format(ayat_id, chat_id))
        query = """
            SELECT COUNT(*)
            FROM favorite_ayats AS fa
            INNER JOIN users AS u ON fa.user_id = u.chat_id
            WHERE fa.ayat_id = :ayat_id AND u.chat_id = :chat_id
        """
        count = await self._connection.fetch_val(query, {'ayat_id': ayat_id, 'chat_id': chat_id})
        logger.debug('Ayat <{0}> is favorite for user <{1}> result: {2}'.format(ayat_id, chat_id, bool(count)))
        return bool(count)
