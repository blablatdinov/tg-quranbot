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
from databases import Database
from pyeo import elegant
from redis.asyncio import Redis

from app_types.update import Update
from integrations.nats_integration import SinkInterface
from integrations.tg.tg_answers import TgAnswer, TgAnswerMarkup, TgAnswerToSender, TgHtmlParseAnswer, TgMessageAnswer
from repository.admin_message import AdminMessage
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.answer import DefaultKeyboard, ResizedKeyboard
from services.register_event import StartWithEventAnswer
from services.reset_state_answer import ResetStateAnswer
from services.start.start_answer import StartAnswer
from services.start.user_already_active import UserAlreadyActiveSafeAnswer
from services.start.user_already_exists import UserAlreadyExistsAnswer
from settings import AdminChatIds, Settings


@attrs.define(frozen=True)
@final
@elegant
class FullStartAnswer(TgAnswer):
    """Ответ на команду /start."""

    _pgsql: Database
    _empty_answer: TgAnswer
    _event_sink: SinkInterface
    _redis: Redis
    _settings: Settings

    async def build(self, update: Update) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Update
        :return: list[httpx.Request]
        """
        answer_to_sender = TgAnswerToSender(TgMessageAnswer(self._empty_answer))
        return await ResetStateAnswer(
            TgAnswerMarkup(
                UserAlreadyActiveSafeAnswer(
                    UserAlreadyExistsAnswer(
                        StartWithEventAnswer(
                            StartAnswer(
                                TgHtmlParseAnswer(
                                    TgMessageAnswer(self._empty_answer),
                                ),
                                UserRepository(self._pgsql),
                                AdminMessage('start', self._pgsql),
                                self._pgsql,
                                AdminChatIds(self._settings),
                            ),
                            self._event_sink,
                            UserRepository(self._pgsql),
                        ),
                        answer_to_sender,
                        UserRepository(self._pgsql),
                        UsersRepository(self._pgsql),
                        self._event_sink,
                    ),
                    answer_to_sender,
                ),
                ResizedKeyboard(
                    DefaultKeyboard(),
                ),
            ),
            self._redis,
        ).build(update)
