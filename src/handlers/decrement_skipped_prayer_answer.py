# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.update import Update
from handlers.prayers_statistic import PrayersStatistic
from handlers.skipped_prayers_keyboard import SkippedPrayersKeyboard
from integrations.tg.callback_query import CallbackQueryData
from integrations.tg.message_id import TgMessageId
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgMessageIdAnswer, TgTextAnswer
from integrations.tg.tg_answers.edit_message_text import TgEditMessageText
from integrations.tg.tg_chat_id import TgChatId
from srv.prayers.pg_new_prayers_at_user import PgNewPrayersAtUser


@final
@attrs.define(frozen=True)
class DecrementSkippedPrayerAnswer(TgAnswer):
    """Уменьшение кол-ва пропущенных намазов."""

    _empty_answer: TgAnswer
    _pgsql: Database

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        query = '\n'.join([
            'UPDATE prayers_at_user AS pau',
            "SET is_read = 't'",
            'WHERE pau.prayer_at_user_id = (',
            '   SELECT pau.prayer_at_user_id',
            '   FROM prayers AS p',
            '   INNER JOIN prayers_at_user AS pau ON pau.prayer_id = p.prayer_id',
            "   WHERE p.name = :prayer_name AND pau.is_read = 'f' AND pau.user_id = :chat_id",
            '   LIMIT 1',
            ')',
            'RETURNING *',
        ])
        await self._pgsql.execute(query, {
            'chat_id': int(TgChatId(update)),
            'prayer_name': str(
                CallbackQueryData(update),
            ).split('(')[1][:-1],
        })
        return await TgAnswerMarkup(
            TgMessageIdAnswer(
                TgTextAnswer(
                    TgEditMessageText(
                        TgAnswerToSender(
                            self._empty_answer,
                        ),
                    ),
                    PrayersStatistic(
                        PgNewPrayersAtUser(TgChatId(update), self._pgsql),
                        TgChatId(update),
                        self._pgsql,
                    ),
                ),
                TgMessageId(update),
            ),
            SkippedPrayersKeyboard(),
        ).build(update)
