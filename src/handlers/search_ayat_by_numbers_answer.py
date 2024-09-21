# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from typing import final, override

import attrs
import httpx
from databases import Database
from redis.asyncio import Redis

from app_types.logger import LogSink
from app_types.supports_bool import SupportsBool
from app_types.update import Update
from integrations.tg.tg_answers import TgAnswer, TgAnswerToSender, TgAudioAnswer
from integrations.tg.tg_answers.message_answer_to_sender import TgHtmlMessageAnswerToSender
from integrations.tg.tg_chat_id import TgChatId
from services.reset_state_answer import ResetStateAnswer
from srv.ayats.ayat_by_sura_ayat_num_answer import AyatBySuraAyatNumAnswer
from srv.ayats.ayat_not_found_safe_answer import AyatNotFoundSafeAnswer
from srv.ayats.sura_not_found_safe_answer import SuraNotFoundSafeAnswer
from srv.users.cached_user_state import CachedUserState
from srv.users.redis_user_state import RedisUserState


@final
@attrs.define(frozen=True)
class SearchAyatByNumbersAnswer(TgAnswer):
    """Поиск аята по номеру суры/аята."""

    _debug_mode: SupportsBool
    _empty_answer: TgAnswer
    _redis: Redis
    _pgsql: Database
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await ResetStateAnswer(
            SuraNotFoundSafeAnswer(
                AyatNotFoundSafeAnswer(
                    AyatBySuraAyatNumAnswer(
                        self._debug_mode,
                        self._empty_answer,
                        TgAnswerToSender(TgAudioAnswer(self._empty_answer)),
                        self._pgsql,
                    ),
                    TgHtmlMessageAnswerToSender(self._empty_answer),
                ),
                TgHtmlMessageAnswerToSender(self._empty_answer),
            ),
            CachedUserState(RedisUserState(self._redis, TgChatId(update), self._logger)),
        ).build(update)
