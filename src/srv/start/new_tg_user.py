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
