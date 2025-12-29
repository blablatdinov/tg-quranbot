# SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final, override

import attrs
from redis.asyncio import Redis

from app_types.logger import LogSink
from integrations.tg.fk_chat_id import ChatId
from srv.users.user_state import UserState
from srv.users.user_step import UserStep


@final
@attrs.define(frozen=True)
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
