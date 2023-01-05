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

from app_types.stringable import Stringable
from exceptions.user import StartMessageNotContainReferrer
from integrations.nats_integration import SinkInterface
from integrations.tg.chat_id import TgChatId
from integrations.tg.message_text import MessageText
from integrations.tg.tg_answers import TgAnswerInterface
from integrations.tg.tg_datetime import TgDateTime
from repository.users.user import UserRepositoryInterface
from services.start.start_message import StartMessage


class StartWithEventAnswer(TgAnswerInterface):
    """Регистрация с отправкой события."""

    def __init__(self, answer: TgAnswerInterface, event_sink: SinkInterface, user_repo: UserRepositoryInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param event_sink: SinkInterface
        :param user_repo: UserRepositoryInterface
        """
        self._origin = answer
        self._event_sink = event_sink
        self._user_repo = user_repo

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            referrer_id = await StartMessage(str(MessageText(update)), self._user_repo).referrer_chat_id()
        except StartMessageNotContainReferrer:
            referrer_id = None
        requests = await self._origin.build(update)
        await self._event_sink.send(
            {
                'user_id': int(TgChatId(update)),
                'referrer_id': referrer_id,
                'date_time': TgDateTime(update).datetime().isoformat(),
            },
            'User.Subscribed',
            1,
        )
        return requests
