from typing import Optional

from loguru import logger
from pydantic import BaseModel, ValidationError

from repository.users.user import UserRepositoryInterface


class StartMessageMeta(BaseModel):
    """Мета информация стартового сообщения."""

    referrer: int


class StartMessageInterface(object):
    """Интерфейс поведения стартового сообщения."""

    async def referrer_id(self) -> Optional[int]:
        """Вычислить идентификатор реферала.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class StartMessage(StartMessageInterface):
    """Класс, имплементирующий поведение стартового сообщения."""

    def __init__(self, message: str, user_repository: UserRepositoryInterface):
        self._message = message
        self._user_repository = user_repository

    async def referrer_id(self) -> Optional[int]:
        """Вычислить идентификатор реферала.

        :return: Optional[int]
        """
        splitted_message = self._message.split(' ')
        if len(splitted_message) == 1:
            return None
        message_raw_meta = ' '.join(splitted_message[1:])
        try:
            ref_id = StartMessageMeta.parse_raw(message_raw_meta).referrer
        except ValidationError:
            ref_id = self._try_parse_int(splitted_message)
            if not ref_id:
                return None
        max_legacy_referrer_id = 3000
        if ref_id < max_legacy_referrer_id:
            return (await self._user_repository.get_by_id(ref_id)).chat_id
        return ref_id

    def _try_parse_int(self, splitted_message: list[str]) -> Optional[int]:
        try:
            return int(splitted_message[1])
        except ValueError:
            logger.error('Start message "{0}" can not be parsed'.format(self._message))
