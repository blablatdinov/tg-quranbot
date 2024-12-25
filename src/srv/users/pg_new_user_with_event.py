# The MIT License (MIT).
#
# Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

from app_types.date_time import DateTime
from integrations.tg.fk_chat_id import ChatId
from srv.events.sink import Sink
from srv.users.new_user import NewUser


@final
@attrs.define(frozen=True)
class PgNewUserWithEvent(NewUser):
    """Создание пользователя с событием."""

    _origin: NewUser
    _event_sink: Sink
    _new_user_chat_id: ChatId
    _datetime: DateTime

    @override
    async def create(self) -> None:
        """Создание."""
        await self._origin.create()
        await self._event_sink.send(
            'qbot_admin.users',
            {
                'user_id': int(self._new_user_chat_id),
                'date_time': str(self._datetime.datetime()),
                'referrer_id': None,
            },
            'User.Subscribed',
            1,
        )
