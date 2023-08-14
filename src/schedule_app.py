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
from pyeo import elegant

from app_types.runable import Runable
from app_types.update import FkUpdate, Update
from integrations.tg.sendable import BulkSendableAnswer
from integrations.tg.tg_answers import TgAnswer, TgChatIdAnswer
from integrations.tg.tg_answers.chat_action import TgChatAction
from repository.users.users import UsersRepositoryInterface


@final
@attrs.define(frozen=True)
@elegant
class TypingAction(TgAnswer):
    """Действие с печатью."""

    _origin: TgAnswer

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

    _users_repo: UsersRepositoryInterface
    _empty_answer: TgAnswer

    async def run(self):
        """Запуск."""
        chat_ids = await self._users_repo.get_active_user_chat_ids()
        deactivated_users = []
        answers: list[TgAnswer] = [
            TypingAction(
                TgChatIdAnswer(
                    TgChatAction(self._empty_answer),
                    chat_id,
                ),
            )
            for chat_id in chat_ids
        ]
        for response_list in await BulkSendableAnswer(answers).send(FkUpdate()):
            for response_dict in response_list:
                if not response_dict['ok']:
                    deactivated_users.append(response_dict['chat_id'])
        await self._users_repo.update_status(list(set(deactivated_users)), to=False)
