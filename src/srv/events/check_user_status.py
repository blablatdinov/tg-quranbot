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

from typing import final, override

import attrs
from databases import Database
from eljson.json import Json

from app_types.fk_update import FkUpdate
from app_types.listable import AsyncListable
from app_types.logger import LogSink
from integrations.tg.bulk_sendable_answer import BulkSendableAnswer
from integrations.tg.tg_answers import TgAnswer, TgChatIdAnswer
from integrations.tg.tg_answers.chat_action import TgChatAction
from integrations.tg.typing_action import TypingAction
from srv.events.recieved_event import ReceivedEvent
from srv.events.sink import Sink
from srv.users.pg_active_users import PgActiveUsers
from srv.users.pg_updated_users_status import PgUpdatedUsersStatus
from srv.users.pg_users import PgUsers
from srv.users.updated_users_status_event import UpdatedUsersStatusEvent
from srv.users.user import User


@final
@attrs.define(frozen=True)
class CheckUsersStatus(ReceivedEvent):
    """Статусы пользователей."""

    _empty_answer: TgAnswer
    _pgsql: Database
    _events_sink: Sink
    _logger: LogSink

    @override
    async def process(self, json_doc: Json) -> None:
        """Обработка события.

        :param json_doc: Json
        """
        users = PgActiveUsers(self._pgsql)
        zipped_user_responses = zip(
            await users.to_list(),
            await BulkSendableAnswer(
                await self._answers(users),
                self._logger,
            ).send(FkUpdate.empty_ctor()),
            strict=True,
        )
        deactivated_user_chat_ids = [
            await user.chat_id()
            for user, response_dict in zipped_user_responses
            if not response_dict['ok']
        ]
        await UpdatedUsersStatusEvent(
            PgUpdatedUsersStatus(
                self._pgsql,
                PgUsers(self._pgsql, deactivated_user_chat_ids),
            ),
            PgUsers(self._pgsql, deactivated_user_chat_ids),
            self._events_sink,
        ).update(to=False)

    async def _answers(self, users: AsyncListable[User]) -> list[TgAnswer]:
        # TODO #802 Удалить или задокументировать необходимость приватного метода "_answers"
        return [
            TypingAction(
                TgChatIdAnswer(
                    TgChatAction(self._empty_answer),
                    await user.chat_id(),
                ),
            )
            for user in await users.to_list()
        ]
