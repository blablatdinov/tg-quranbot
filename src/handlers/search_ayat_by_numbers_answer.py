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
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerToSender, TgAudioAnswer, TgHtmlParseAnswer, TgMessageAnswer
from services.reset_state_answer import ResetStateAnswer
from srv.ayats.ayat_by_sura_ayat_num_answer import AyatBySuraAyatNumAnswer
from srv.ayats.ayat_not_found_safe_answer import AyatNotFoundSafeAnswer
from srv.ayats.sura_not_found_safe_answer import SuraNotFoundSafeAnswer


@final
@attrs.define(frozen=True)
@elegant
class SearchAyatByNumbersAnswer(TgAnswer):
    """Поиск аята по номеру суры/аята."""

    _debug: bool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        html_to_sender = TgAnswerToSender(
            TgHtmlParseAnswer(TgMessageAnswer(self._empty_answer)),
        )
        audio_to_sender = TgAnswerToSender(TgAudioAnswer(self._empty_answer))
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await ResetStateAnswer(
            SuraNotFoundSafeAnswer(
                AyatNotFoundSafeAnswer(
                    AyatBySuraAyatNumAnswer(
                        self._debug,
                        html_to_sender,
                        audio_to_sender,
                        self._pgsql,
                    ),
                    answer_to_sender,
                ),
                answer_to_sender,
            ),
            self._redis,
        ).build(update)
