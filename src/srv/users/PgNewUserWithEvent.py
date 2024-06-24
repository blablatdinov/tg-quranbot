from app_types.date_time import DateTime
from integrations.tg.chat_id import ChatId
from srv.events.sink import Sink
from srv.users.new_user import NewUser


import attrs
from pyeo import elegant


from typing import final, override


@final
@attrs.define(frozen=True)
@elegant
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