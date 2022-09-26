import enum
import json

from aioredis import Redis
from loguru import logger


class UserStep(enum.Enum):
    city_search = 'city_search'
    nothing = 'nothing'


class UserStateInterface(object):

    async def step(self):
        raise NotImplementedError

    async def change_step(self, step: UserStep):
        raise NotImplementedError


class LoggedUserState(UserStateInterface):

    def __init__(self, user_state: UserStateInterface):
        self._origin = user_state

    async def step(self) -> UserStep:
        res = await self._origin.step()
        logger.info('User state: {0}'.format(res))
        return res

    async def change_step(self, step: UserStep):
        logger.info('Setting user state...')
        await self._origin.change_step(step)
        logger.info('State {0} setted'.format(step))


class UserState(UserStateInterface):

    def __init__(self, redis: Redis, chat_id: int):
        self._redis = redis
        self._chat_id = chat_id

    async def step(self) -> UserStep:
        redis_state_data = await self._redis.get('{0}_state'.format(self._chat_id))
        if not redis_state_data:
            return UserStep.nothing
        return UserStep(
            json.loads(redis_state_data)['step']
        )

    async def change_step(self, step: UserStep):
        await self._redis.set(
            '{0}_state'.format(self._chat_id),
            json.dumps({'step': step.value}),
        )
