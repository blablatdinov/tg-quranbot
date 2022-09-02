from typing import Optional

from loguru import logger
from pydantic import BaseModel, ValidationError

from repository.users.user import UserRepositoryInterface


class StartMessageMeta(BaseModel):
    """Мета информация стартового сообщения."""

    referrer: int


class StartMessageInterface(object):

    async def referrer_id(self) -> Optional[int]:
        raise NotImplementedError


class StartMessage(StartMessageInterface):

    def __init__(self, message: str, user_repository: UserRepositoryInterface):
        self._message = message
        self._user_repository = user_repository

    async def referrer_id(self) -> Optional[int]:
        splitted_message = self._message.split(' ')
        if len(splitted_message) == 1:
            return
        message_raw_meta = ' '.join(splitted_message[1:])
        try:
            ref_id = StartMessageMeta.parse_raw(message_raw_meta).referrer
        except ValidationError:
            try:
                ref_id = int(splitted_message[1])
            except ValueError:
                logger.error('Start message "{0}" can not be parsed'.format(self._message))
                return
        max_legacy_referrer_id = 3000
        if ref_id < max_legacy_referrer_id:
            return (await self._user_repository.get_by_id(ref_id)).chat_id
        return ref_id
