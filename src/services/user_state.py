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
from typing import Protocol

from aioredis import Redis
from loguru import logger


class UserStep(enum.Enum):
    """Перечисление возможных состояний пользователя."""

    city_search = 'city_search'
    nothing = 'nothing'
    ayat_search = 'ayat_search'


class UserStateInterface(Protocol):
    """Интерфейс для работы с состоянием пользователя."""

    async def step(self) -> UserStep:
        """Состояние пользователя."""

    async def change_step(self, step: UserStep):
        """Изменение, состояние пользователя.

        :param step: UserStep
        """


class LoggedUserState(UserStateInterface):
    """Логгирующий декоратор объекта, работающего с состоянием пользователя."""

    def __init__(self, user_state: UserStateInterface):
        """Конструктор класса.

        :param user_state: UserStateInterface
        """
        self._origin = user_state

    async def step(self) -> UserStep:
        """Состояние пользователя.

        :return: UserStep
        """
        res = await self._origin.step()
        logger.info('User state: {0}'.format(res))
        return res

    async def change_step(self, step: UserStep):
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
        logger.info('Setting user state...')
        await self._origin.change_step(step)
        logger.info('State {0} setted'.format(step))


class UserState(UserStateInterface):
    """Объект, работающий с состоянием пользователя."""

    def __init__(self, redis: Redis, chat_id: int):
        """Конструктор класса.

        :param redis: Redis
        :param chat_id: int
        """
        self._redis = redis
        self._chat_id = chat_id

    async def step(self) -> UserStep:
        """Состояние пользователя.

        :return: UserStep
        """
        redis_state_data = (
            await self._redis.get('{0}:step'.format(self._chat_id))
        )
        if not redis_state_data:
            return UserStep.nothing
        return UserStep[redis_state_data.decode('utf-8')]

    async def change_step(self, step: UserStep):
        """Изменение, состояние пользователя.

        :param step: UserStep
        """
        await self._redis.set(
            '{0}:step'.format(self._chat_id),
            step.value,
        )
