# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import Final, final, override

import attrs
import httpx
from databases import Database

from app_types.update import Update
from handlers.prayers_statistic import PrayersStatistic
from handlers.skipped_prayers_keyboard import SkippedPrayersKeyboard
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgMessageAnswer, TgTextAnswer
from integrations.tg.tg_chat_id import TgChatId
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser

IS_READ_LITERAL: Final = 'is_read'


@final
@attrs.define(frozen=True)
class SkippedPrayersAnswer(TgAnswer):
    """Пропущенные намазы."""

    _empty_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return await TgAnswerMarkup(
            TgTextAnswer(
                TgAnswerToSender(
                    TgMessageAnswer(self._empty_answer),
                ),
                PrayersStatistic(
                    PgNewPrayersAtUser(TgChatId(update), self._pgsql),
                    TgChatId(update),
                    self._pgsql,
                ),
            ),
            SkippedPrayersKeyboard(),
        ).build(update)
