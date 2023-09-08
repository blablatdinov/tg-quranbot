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
from collections.abc import Sequence
from contextlib import suppress
from typing import final

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.intable import ThroughAsyncIntable
from app_types.update import Update
from exceptions.user import StartMessageNotContainReferrer, UserAlreadyExists
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswer, TgAnswerList, TgAnswerToSender, TgChatIdAnswer, TgTextAnswer
from repository.users.user import UserRepositoryInterface
from services.start.start_message import SmartReferrerChatId
from srv.admin_messages.admin_message import AdminMessage
from srv.ayats.pg_ayat import PgAyat


@final
@attrs.define(frozen=True)
@elegant
class StartAnswer(TgAnswer):
    """Обработчик стартового сообщения."""

    _origin: TgAnswer
    _user_repo: UserRepositoryInterface
    _admin_message: AdminMessage
    _pgsql: Database
    _admin_chat_ids: Sequence[int]

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        await self._check_user_exists(update)
        await self._user_repo.create(int(TgChatId(update)))
        start_message, ayat_message = await self._start_answers()
        create_with_referrer_answers = await self._create_with_referrer(update, start_message, ayat_message)
        if create_with_referrer_answers:
            return create_with_referrer_answers
        return await TgAnswerList(
            TgAnswerToSender(
                TgTextAnswer.str_ctor(
                    self._origin,
                    start_message,
                ),
            ),
            TgAnswerToSender(
                TgTextAnswer.str_ctor(
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

    async def _start_answers(self) -> tuple[str, str]:
        return (
            await self._admin_message.text(),
            await PgAyat(ThroughAsyncIntable(1), self._pgsql).text(),
        )

    async def _check_user_exists(self, update: Update) -> None:
        if await self._user_repo.exists(int(TgChatId(update))):
            raise UserAlreadyExists

    async def _create_with_referrer(self, update, start_message, ayat_message) -> list[httpx.Request]:
        with suppress(StartMessageNotContainReferrer):
            referrer_id = await SmartReferrerChatId(str(MessageText(update)), self._user_repo).to_int()
            await self._user_repo.update_referrer(int(TgChatId(update)), referrer_id)
            return await TgAnswerList(
                TgAnswerToSender(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        start_message,
                    ),
                ),
                TgAnswerToSender(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        ayat_message,
                    ),
                ),
                TgChatIdAnswer(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        'По вашей реферальной ссылке произошла регистрация',
                    ),
                    referrer_id,
                ),
                TgChatIdAnswer(
                    TgTextAnswer.str_ctor(
                        self._origin,
                        'Зарегистрировался новый пользователь',
                    ),
                    self._admin_chat_ids[0],
                ),
            ).build(update)
        return []
