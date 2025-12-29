# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
