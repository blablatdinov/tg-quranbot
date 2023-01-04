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
import httpx

from app_types.runable import Runable
from app_types.stringable import Stringable
from integrations.tg.sendable import BulkSendableAnswer
from integrations.tg.tg_answers import TgAnswerInterface, TgChatIdAnswer
from integrations.tg.tg_answers.chat_action import TgChatAction
from integrations.tg.tg_answers.update import Update
from repository.users.users import UsersRepositoryInterface


class TypingAction(TgAnswerInterface):
    """Действие с печатью."""

    def __init__(self, answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        """
        self._origin = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                method=request.method, url=request.url.copy_add_param('action', 'typing'), headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]


class CheckUsersStatus(Runable):
    """Статусы пользователей."""

    def __init__(self, users_repo: UsersRepositoryInterface, empty_answer: TgAnswerInterface):
        """Конструктор класса.

        :param users_repo: UsersRepositoryInterface
        :param empty_answer: TgAnswerInterface
        """
        self._users_repo = users_repo
        self._empty_answer = empty_answer

    async def run(self):
        """Запуск."""
        chat_ids = await self._users_repo.get_active_user_chat_ids()
        deactivated_users = []
        answers: list[TgAnswerInterface] = [
            TypingAction(
                TgChatIdAnswer(
                    TgChatAction(self._empty_answer),
                    chat_id,
                ),
            )
            for chat_id in chat_ids
        ]
        for response_list in await BulkSendableAnswer(answers).send(Update(update_id=0)):
            for response_dict in response_list:
                if not response_dict['ok']:
                    deactivated_users.append(response_dict['chat_id'])
        await self._users_repo.update_status(list(set(deactivated_users)), to=False)


# class ScheduleApp(Runable):
#
#     async def run(self) -> None:
