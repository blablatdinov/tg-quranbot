"""The MIT License (MIT).

Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

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
from typing import final, override

import attrs
import httpx
from databases import Database
from pyeo import elegant

from app_types.listable import AsyncListable
from app_types.logger import LogSink
from app_types.runable import Runable
from app_types.update import FkUpdate, Update
from integrations.tg.sendable import BulkSendableAnswer
from integrations.tg.tg_answers import TgAnswer, TgChatIdAnswer
from integrations.tg.tg_answers.chat_action import TgChatAction
from srv.users.active_users import ActiveUsers, PgUpdatedUsersStatus, PgUsers
from srv.users.pg_user import User


@final
@attrs.define(frozen=True)
@elegant
class TypingAction(TgAnswer):
    """Действие с печатью."""

    _origin: TgAnswer

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                method=request.method, url=request.url.copy_add_param('action', 'typing'), headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]


@final
@attrs.define(frozen=True)
@elegant
class CheckUsersStatus(Runable):
    """Статусы пользователей."""

    _pgsql: Database
    _empty_answer: TgAnswer
    _logger: LogSink

    @override
    async def run(self) -> None:
        """Запуск."""
        users = ActiveUsers(self._pgsql)
        zipped_user_responses = zip(
            await users.to_list(),
            await BulkSendableAnswer(await self._answers(users), self._logger).send(FkUpdate()),
            strict=True,
        )
        deactivated_user_chat_ids = [
            await user.chat_id()
            for user, response_dict in zipped_user_responses
            if not response_dict['ok']
        ]
        await PgUpdatedUsersStatus(
            self._pgsql,
            PgUsers(self._pgsql, deactivated_user_chat_ids),
        ).update(to=False)

    async def _answers(self, users: AsyncListable[User]) -> list[TgAnswer]:
        return [
            TypingAction(
                TgChatIdAnswer(
                    TgChatAction(self._empty_answer),
                    await user.chat_id(),
                ),
            )
            for user in await users.to_list()
        ]
