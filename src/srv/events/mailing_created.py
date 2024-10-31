# The MIT License (MIT).
#
# Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

import uuid
from typing import final, override

import attrs
from databases import Database
from eljson.json import Json

from app_types.fk_async_listable import FkAsyncListable
from app_types.fk_update import FkUpdate
from app_types.logger import LogSink
from exceptions.internal_exceptions import TelegramIntegrationsError, UnreacheableError
from integrations.tg.sendable_answer import SendableAnswer
from integrations.tg.tg_answers import TgAnswer, TgChatIdAnswer, TgHtmlParseAnswer, TgTextAnswer
from integrations.tg.tg_answers.message_answer import TgMessageAnswer
from services.logged_answer import LoggedAnswer
from settings import Settings
from srv.events.recieved_event import ReceivedEvent
from srv.events.sink import Sink
from srv.users.fk_user import FkUser
from srv.users.pg_updated_users_status import PgUpdatedUsersStatus
from srv.users.updated_users_status_event import UpdatedUsersStatusEvent
from srv.users.user import User


@final
@attrs.define(frozen=True)
class MailingCreatedEvent(ReceivedEvent):
    """Обработка события об утренней рассылки с аятми."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _events_sink: Sink
    _log_sink: LogSink
    _settings: Settings

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработка события.

        :param json_doc: Json
        :raises UnreacheableError: unreacheable state
        """
        if json_doc.path('$.data.group')[0] == 'all':
            chat_ids = [
                row['chat_id']
                for row in await self._pgsql.fetch_all('\n'.join([
                    'SELECT chat_id',
                    'FROM users',
                    "WHERE is_active = 't'",
                ]))
            ]
        elif json_doc.path('$.data.group')[0] == 'admins':
            chat_ids = self._settings.admin_chat_ids()
        else:
            raise UnreacheableError
        unsubscribed_users: list[User] = []
        zipped_ans_chat_ids = zip(
            [
                TgHtmlParseAnswer(
                    TgTextAnswer.str_ctor(
                        TgChatIdAnswer(
                            TgMessageAnswer(self._empty_answer),
                            chat_id,
                        ),
                        json_doc.path('$.data.text')[0],
                    ),
                )
                for chat_id in chat_ids
            ],
            chat_ids,
            strict=True,
        )
        for answer, chat_id in zipped_ans_chat_ids:
            await self._iteration(answer, chat_id, unsubscribed_users, json_doc.path('$.data.mailing_id')[0])
        await UpdatedUsersStatusEvent(
            PgUpdatedUsersStatus(self._pgsql, FkAsyncListable(unsubscribed_users)),
            FkAsyncListable(unsubscribed_users),
            self._events_sink,
        ).update(to=False)

    async def _iteration(  # noqa: NPM100. Fix it
        self,
        answer: TgAnswer,
        chat_id: int,
        unsubscribed_users: list[User],
        mailing_id: uuid.UUID,
    ) -> None:
        try:
            await LoggedAnswer(
                SendableAnswer(
                    answer,
                    self._log_sink,
                ),
                self._events_sink,
                mailing_id,
            ).send(FkUpdate.empty_ctor())
        except TelegramIntegrationsError as err:
            error_messages = [
                'chat not found',
                'bot was blocked by the user',
                'user is deactivated',
            ]
            for error_message in error_messages:
                if error_message in str(err):
                    unsubscribed_users.append(FkUser(chat_id, 0, is_active=False))  # noqa: PERF401
