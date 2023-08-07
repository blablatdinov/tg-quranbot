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

from app_types.update import Update
from integrations.nats_integration import SinkInterface
from integrations.tg.tg_answers import TgAnswerInterface, TgAnswerMarkup, TgHtmlParseAnswer, TgMessageAnswer
from repository.admin_message import AdminMessage
from repository.users.user import UserRepository
from repository.users.users import UsersRepository
from services.answers.answer import DefaultKeyboard, ResizedKeyboard
from services.register_event import StartWithEventAnswer
from services.start.start_answer import StartAnswer
from services.start.user_already_active import UserAlreadyActiveSafeAnswer
from services.start.user_already_exists import UserAlreadyExistsAnswer


@attrs.define(frozen=True)
@final
@elegant
class FullStartAnswer(TgAnswerInterface):

    _database: Database
    _empty_answer: TgAnswerInterface
    _event_sink: SinkInterface
    _answer_to_sender: TgAnswerInterface

    async def build(self, update: Update) -> list[httpx.Request]:
        return await TgAnswerMarkup(
            UserAlreadyActiveSafeAnswer(
                UserAlreadyExistsAnswer(
                    StartWithEventAnswer(
                        StartAnswer(
                            TgHtmlParseAnswer(
                                TgMessageAnswer(self._empty_answer),
                            ),
                            UserRepository(self._database),
                            AdminMessage('start', self._database),
                            self._database,
                        ),
                        self._event_sink,
                        UserRepository(self._database),
                    ),
                    self._answer_to_sender,
                    UserRepository(self._database),
                    UsersRepository(self._database),
                    self._event_sink,
                ),
                self._answer_to_sender,
            ),
            ResizedKeyboard(
                DefaultKeyboard(),
            ),
        ).build(update)
