# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from databases import Database

from app_types.async_int_or_none import AsyncIntOrNone
from app_types.fk_async_int_or_none import FkAsyncIntOrNone
from app_types.logger import LogSink
from app_types.update import Update
from exceptions.internal_exceptions import UserNotFoundError
from integrations.tg.tg_chat_id import TgChatId
from integrations.tg.tg_datetime import TgDateTime
from srv.events.sink import Sink
from srv.start.new_user import NewUser
from srv.users.pg_new_user import PgNewUser
from srv.users.pg_new_user_with_event import PgNewUserWithEvent


@final
@attrs.define(frozen=True)
class NewTgUser(NewUser):
    """Registration of user by tg."""

    _pgsql: Database
    _logger: LogSink
    _event_sink: Sink
    _update: Update

    @override
    async def create(self, referrer_chat_id: AsyncIntOrNone) -> None:
        """Creation.

        :param referrer_chat_id: AsyncIntOrNone
        """
        try:
            await PgNewUserWithEvent(
                PgNewUser(
                    referrer_chat_id,
                    TgChatId(self._update),
                    self._pgsql,
                    self._logger,
                ),
                self._event_sink,
                TgChatId(self._update),
                TgDateTime(self._update),
            ).create()
        except UserNotFoundError:
            referrer_chat_id = FkAsyncIntOrNone(None)
            await PgNewUserWithEvent(
                PgNewUser(
                    referrer_chat_id,
                    TgChatId(self._update),
                    self._pgsql,
                    self._logger,
                ),
                self._event_sink,
                TgChatId(self._update),
                TgDateTime(self._update),
            ).create()
