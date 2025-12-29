# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from contextlib import suppress
from typing import final, override

import attrs
import httpx
from databases import Database

from app_types.update import Update
from exceptions.user import UserAlreadyActiveError, UserAlreadyExistsError
from integrations.tg.tg_answers import TgAnswer, TgTextAnswer
from integrations.tg.tg_chat_id import TgChatId
from integrations.tg.tg_datetime import TgDateTime
from srv.events.sink import Sink
from srv.users.pg_updated_users_status import PgUpdatedUsersStatus
from srv.users.pg_user import PgUser
from srv.users.pg_users import PgUsers
from srv.users.pg_valid_chat_id import PgValidChatId


@final
@attrs.define(frozen=True)
class UserAlreadyExistsAnswer(TgAnswer):
    """Декоратор обработчика стартового сообщение с предохранением от UserAlreadyExists."""

    _origin: TgAnswer
    _sender_answer: TgAnswer
    _pgsql: Database
    _event_sink: Sink

    @override
    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        :raises UserAlreadyActiveError: if user already active
        """
        with suppress(UserAlreadyExistsError):
            return await self._origin.build(update)
        user = PgUser(PgValidChatId.int_ctor(self._pgsql, TgChatId(update)), self._pgsql)
        await self._update_and_push_event(update)
        if await user.is_active():
            raise UserAlreadyActiveError
        return await TgTextAnswer.str_ctor(
            self._sender_answer,
            'Рады видеть вас снова, вы продолжите с дня {0}'.format(await user.day()),
        ).build(update)

    async def _update_and_push_event(self, update: Update) -> None:  # noqa: NPM100. Fix it
        await PgUpdatedUsersStatus(
            self._pgsql,
            PgUsers(self._pgsql, [int(TgChatId(update))]),
        ).update(to=True)
        await self._event_sink.send(
            'qbot_admin.users',
            {
                'user_id': int(TgChatId(update)),
                'date_time': str(TgDateTime(update).datetime()),
            },
            'User.Reactivated',
            1,
        )
