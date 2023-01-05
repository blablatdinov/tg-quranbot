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
import httpx

from app_types.stringable import Stringable
from db.connection import database
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerInterface
from repository.ayats.favorite_ayats import FavoriteAyatsRepository
from repository.ayats.neighbor_ayats import NeighborAyats
from services.ayats.ayat_answer import AyatAnswer
from services.ayats.ayat_keyboard_callback_template import AyatCallbackTemplate
from services.ayats.ayat_search_interface import AyatSearchInterface
from services.ayats.keyboards import AyatAnswerKeyboard


class AyatBySuraAyatNumAnswer(TgAnswerInterface):
    """Ответ на поиск аята по номеру суры, аята."""

    def __init__(
        self,
        debug_mode: bool,
        message_answer: TgAnswerInterface,
        file_answer: TgAnswerInterface,
        ayat_search: AyatSearchInterface,
    ):
        """Конструктор класса.

        :param debug_mode: bool
        :param message_answer: TgAnswerInterface
        :param file_answer: TgAnswerInterface
        :param ayat_search: AyatSearchInterface
        """
        self._debug_mode = debug_mode
        self._message_answer = message_answer
        self._file_answer = file_answer
        self._ayat_search = ayat_search

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        result_ayat = await self._ayat_search.search(str(MessageText(update)))
        answers = (self._message_answer, self._file_answer)
        return await AyatAnswer(
            self._debug_mode,
            answers,
            result_ayat,
            AyatAnswerKeyboard(
                result_ayat,
                FavoriteAyatsRepository(database),
                NeighborAyats(database, result_ayat.id),
                AyatCallbackTemplate.get_ayat,
            ),
        ).build(update)
