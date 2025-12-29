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
from integrations.tg.tg_answers import TgAnswer, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from services.answers.change_state_answer import ChangeStateAnswer
from srv.ayats.favorite_ayat_answer import FavoriteAyatAnswer
from srv.ayats.favorite_ayat_empty_safe import FavoriteAyatEmptySafeAnswer
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
class FavoriteAyatsAnswer(TgAnswer):
    """Ответ с временами намаза."""

    _debug_mode: SupportsBool
    _pgsql: Database
    _redis: Redis
    _empty_answer: TgAnswer
    _logger: LogSink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await ChangeStateAnswer(
            FavoriteAyatEmptySafeAnswer(
                FavoriteAyatAnswer(
                    self._debug_mode,
                    self._empty_answer,
                    self._pgsql,
                ),
                TgTextAnswer.str_ctor(
                    answer_to_sender,
                    'Вы еще не добавляли аятов в избранное',
                ),
            ),
            self._redis,
            UserStep.ayat_favor,
            self._logger,
        ).build(update)
