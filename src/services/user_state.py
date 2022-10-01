import enum

from aioredis import Redis
from loguru import logger


class UserStep(enum.Enum):
    """Перечисление возможных состояний пользователя."""

    city_search = 'city_search'
    nothing = 'nothing'
    ayat_search = 'ayat_search'


class UserStateInterface(object):
    """Интерфейс для работы с состоянием пользователя."""

    async def step(self) -> UserStep:
        """Состояние пользователя.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def change_step(self, step: UserStep):
        """Изменение, состояние пользователя.

        :param step: UserStep
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class LoggedUserState(UserStateInterface):
    """Логгирующий декоратор объекта, работающего с состоянием пользователя."""

    def __init__(self, user_state: UserStateInterface):
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
