# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

from collections.abc import Sequence
from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.async_int_or_none import AsyncIntOrNone
from app_types.update import Update
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgAnswerToSender, TgChatIdAnswer, TgTextAnswer
from srv.admin_messages.admin_message import AdminMessage
from srv.ayats.pg_ayat import PgAyat
from srv.start.new_user import NewUser
from srv.start.referrer_chat_id import ReferrerChatId
from srv.start.referrer_id_or_none import ReferrerIdOrNone


@final
@attrs.define(frozen=True)
class StartAnswer(TgAnswer):
    """Обработчик стартового сообщения."""

    _origin: TgAnswer
    _admin_message: AdminMessage
    _new_tg_user: NewUser
    _pgsql: Database
    _admin_chat_ids: Sequence[int]

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        referrer_chat_id: AsyncIntOrNone = ReferrerIdOrNone(
            ReferrerChatId(
                str(MessageText(update)),
                self._pgsql,
            ),
        )
        start_message = self._admin_message
        ayat_message = PgAyat.from_int(1, self._pgsql)
        await self._new_tg_user.create(referrer_chat_id)
        referrer_chat_id_calculated = await referrer_chat_id.to_int()
        if referrer_chat_id_calculated:
            return await TgAnswerList.ctor(
                TgAnswerToSender(
                    TgTextAnswer(
                        self._origin,
                        start_message,
                    ),
                ),
                TgAnswerToSender(
                    TgTextAnswer(
                        self._origin,
                        ayat_message,
                    ),
                ),
                TgChatIdAnswer(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        'По вашей реферальной ссылке произошла регистрация',
                    ),
                    referrer_chat_id_calculated,
                ),
                TgChatIdAnswer(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        'Зарегистрировался новый пользователь',
                    ),
                    self._admin_chat_ids[0],
                ),
            ).build(update)
        return await TgAnswerList.ctor(
            TgAnswerToSender(
                TgTextAnswer(
                    self._origin,
                    start_message,
                ),
            ),
            TgAnswerToSender(
                TgTextAnswer(
                    self._origin,
                    ayat_message,
                ),
            ),
            TgChatIdAnswer(
                TgTextAnswer.str_ctor(
                    self._origin,
                    'Зарегистрировался новый пользователь',
                ),
                self._admin_chat_ids[0],
            ),
        ).build(update)
