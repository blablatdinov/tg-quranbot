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
from pyeo import elegant
from redis.asyncio import Redis

from app_types.logger import LogSink
from integrations.tg.fk_chat_id import ChatId
from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
@elegant
class RedisUserState(UserState):
    """Объект, работающий с состоянием пользователя."""

    _redis: Redis
    _chat_id: ChatId
    _logger: LogSink

    @override
    async def step(self) -> UserStep:
        """Состояние пользователя.

        :return: UserStep
        """
        redis_state_data = await self._redis.get('{0}:step'.format(int(self._chat_id)))
        if not redis_state_data:
            return UserStep.nothing
        self._logger.info('User state: {0}'.format(redis_state_data.decode('utf-8')))
        return UserStep[redis_state_data.decode('utf-8')]

    @override
    async def change_step(self, step: UserStep) -> None:
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
        self._logger.info('Setting user <{0}> state <{1}>...'.format(int(self._chat_id), step))
        await self._redis.set(
            '{0}:step'.format(int(self._chat_id)),
            step.value,
        )
        self._logger.info('State {0} for user {1} setted'.format(step, int(self._chat_id)))
