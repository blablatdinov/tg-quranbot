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
from typing import final

import attrs
import httpx
from pyeo import elegant
from redis.asyncio import Redis

from app_types.stringable import ThroughString
from db.connection import database
from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswer
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import TextSearchNeighborAyatsRepository
from services.regular_expression import IntableRegularExpression
from srv.ayats.ayat_answer import AyatAnswer
from srv.ayats.ayat_answer_keyboard import AyatAnswerKeyboard
from srv.ayats.ayat_callback_template_enum import AyatCallbackTemplateEnum
from srv.ayats.ayat_text_search_query import AyatTextSearchQuery
from srv.ayats.ayats_by_text_query import AyatsByTextQuery


@final
@attrs.define(frozen=True)
@elegant
class SearchAyatByTextCallbackAnswer(TgAnswer):
    """Поиск аята по тексту для обработки нажатия кнопки."""

    _debug_mode: bool
    _message_answer: TgAnswer
    _file_answer: TgAnswer
    _redis: Redis

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises AyatNotFoundError: if ayat not found
        """
        target_ayat_id = int(IntableRegularExpression(str(CallbackQueryData(update))))
        try:
            ayats = await AyatsByTextQuery(
                ThroughString(
                    await AyatTextSearchQuery.for_reading_cs(
                        self._redis,
                        int(TgChatId(update)),
                    ).read(),
                ),
                database,
            ).to_list()
        except IndexError as err:
            raise AyatNotFoundError from err
        for ayat in ayats:
            if await ayat.id() == target_ayat_id:
                result_ayat = ayat
                break
        else:
            raise AyatNotFoundError
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                FavoriteAyatsRepository(database),
                TextSearchNeighborAyatsRepository(
                    database,
                    await result_ayat.id(),
                    AyatTextSearchQuery.for_reading_cs(
                        self._redis,
                        int(TgChatId(update)),
                    ),
                ),
                AyatCallbackTemplateEnum.get_search_ayat,
            ),
        ).build(update)
