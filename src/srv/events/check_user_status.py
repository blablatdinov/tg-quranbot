# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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

    async def _answers(self, users: AsyncListable[User]) -> list[TgAnswer]:  # noqa: NPM100. Fix it
        return [
            TypingAction(
                TgChatIdAnswer(
                    TgChatAction(self._empty_answer),
                    await user.chat_id(),
                ),
            )
            for user in await users.to_list()
        ]
