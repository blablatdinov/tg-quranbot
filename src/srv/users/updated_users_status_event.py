import datetime
from typing import final, override

import attrs
import pytz
from pyeo import elegant

from app_types.listable import AsyncListable
from srv.events.sink import Sink
from srv.users.updated_users_status import UpdatedUsersStatus
from srv.users.user import User


@final
@attrs.define(frozen=True)
@elegant
class UpdatedUsersStatusEvent(UpdatedUsersStatus):
    """Событие об отписке."""

    _origin: UpdatedUsersStatus
    _users: AsyncListable[User]
    _events_sink: Sink

    @override
    async def update(self, to: bool) -> None:
        """Обновление.

        :param to: bool
        """
        for user in await self._users.to_list():
            await self._events_sink.send(
                'qbot_admin.users',
                {
                    'user_id': await user.chat_id(),
                    'date_time': str(datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))),
                },
                'User.Unsubscribed',
                1,
            )
        await self._origin.update(to)
