# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

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
