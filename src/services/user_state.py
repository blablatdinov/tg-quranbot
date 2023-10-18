"""The MIT License (MIT).

Copyright (c) 2018-2023 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.
"""
import enum
from typing import Protocol, final, override

import attrs
from loguru import logger
from pyeo import elegant
from redis.asyncio import Redis

from integrations.tg.chat_id import ChatId


@final
class UserStep(enum.Enum):
    """Перечисление возможных состояний пользователя."""

    city_search = 'city_search'
    nothing = 'nothing'
    ayat_search = 'ayat_search'
    ayat_favour = 'ayat_favour'


@elegant
class UserState(Protocol):
    """Интерфейс для работы с состоянием пользователя."""

    async def step(self) -> UserStep:
        """Состояние пользователя."""

    async def change_step(self, step: UserStep) -> None:
        """Изменение, состояние пользователя.

        :param step: UserStep
        """


@final
@elegant
class CachedUserState(UserState):
    """Кэширующий декоратор."""

    @override
    def __init__(self, origin: UserState) -> None:
        """Ctor.

        :param origin: UserState
        """
        self._origin = origin
        self._cache: UserStep | None = None

    @override
    async def step(self) -> UserStep:
        """Состояние пользователя.

        :return: UserStep
        """
        if self._cache:
            return self._cache
        self._cache = await self._origin.step()
        return self._cache

    @override
    async def change_step(self, step: UserStep) -> None:
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
        await self._origin.change_step(step)
        self._cache = step


@final
@attrs.define(frozen=True)
@elegant
class RedisUserState(UserState):
    """Объект, работающий с состоянием пользователя."""

    _redis: Redis
    _chat_id: ChatId

    @override
    async def step(self) -> UserStep:
        """Состояние пользователя.

        :return: UserStep
        """
        redis_state_data = await self._redis.get('{0}:step'.format(int(self._chat_id)))
        if not redis_state_data:
            return UserStep.nothing
        logger.info('User state: {0}'.format(redis_state_data.decode('utf-8')))
        return UserStep[redis_state_data.decode('utf-8')]

    @override
    async def change_step(self, step: UserStep) -> None:
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
        logger.info('Setting user <{0}> state <{1}>...'.format(int(self._chat_id), step))
        await self._redis.set(
            '{0}:step'.format(int(self._chat_id)),
            step.value,
        )
        logger.info('State {0} for user {1} setted'.format(step, int(self._chat_id)))
