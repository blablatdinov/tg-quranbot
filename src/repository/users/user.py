import uuid
from typing import Optional

from databases import Database
from loguru import logger
from pydantic import BaseModel

from exceptions.base_exception import InternalBotError
from exceptions.internal_exceptions import UserNotFoundError


class User(BaseModel):
    """Модель пользователя."""

    is_active: bool
    day: int
    referrer: Optional[int] = None
    chat_id: int
    legacy_id: Optional[int] = None
    city_id: Optional[uuid.UUID]


class UserRepositoryInterface(object):
    """Интерфейс репозитория для работы с пользователями."""

    async def create(self, chat_id: int, referrer_id: Optional[int] = None):
        """Метод для создания пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_by_chat_id(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get_by_id(self, user_id: int) -> User:
        """Метод для получения пользователя.

        :param user_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def update_city(self, chat_id: int, city_id: uuid.UUID):
        """Обновить город пользователя.

        :param chat_id: int
        :param city_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def update_referrer(self, chat_id: int, referrer_id: int):
        """Обновить город пользователя.

        :param chat_id: int
        :param referrer_id: [int]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UserRepository(UserRepositoryInterface):
    """Репозиторий для работы с пользователями."""

    def __init__(self, connection: Database):
        self.connection = connection

    async def create(self, chat_id: int, referrer_id: Optional[int] = None) -> User:
        """Метод для создания пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        :returns: User
        :raises InternalBotError: if connection not return created user values
        """
        logger.debug('Insert in DB User <{0}>...'.format(chat_id))
        query = """
            INSERT INTO
            users (chat_id, referrer_id, day)
            VALUES (:chat_id, :referrer_id, 2)
            RETURNING (chat_id, referrer_id)
        """
        query_return_value = await self.connection.fetch_one(query, {'chat_id': chat_id, 'referrer_id': referrer_id})
        if not query_return_value:
            raise InternalBotError
        logger.debug('User <{0}> inserted in DB'.format(chat_id))
        row = dict(query_return_value._mapping)['row']  # noqa: WPS437
        return User(
            is_active=True,
            day=2,
            referrer=row[1],
            chat_id=row[0],
            city_id=None,
        )

    async def get_by_chat_id(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :returns: User
        :raises UserNotFoundError: возбуждается если пользователь с переданным идентификатором не найден
        """
        query = """
            SELECT
                chat_id,
                is_active,
                day,
                referrer_id as referrer,
                city_id
            FROM users
            WHERE chat_id = :chat_id
        """
        record = await self.connection.fetch_one(query, {'chat_id': chat_id})
        if not record:
            raise UserNotFoundError('Пользователь с chat_id: {0} не найден'.format(chat_id))
        return User.parse_obj(dict(record._mapping))  # noqa: WPS437

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :returns: bool
        """
        query = 'SELECT COUNT(*) FROM users WHERE chat_id = :chat_id'
        count = await self.connection.fetch_val(query, {'chat_id': chat_id})
        return bool(count)

    async def update_city(self, chat_id: int, city_id: uuid.UUID):
        """Обновить город пользователя.

        :param chat_id: int
        :param city_id: uuid.UUID
        """
        query = """
            UPDATE users
            SET city_id = :city_id
            WHERE chat_id = :chat_id
        """
        await self.connection.execute(query, {'city_id': str(city_id), 'chat_id': chat_id})

    async def update_referrer(self, chat_id: int, referrer_id: int):
        """Обновить город пользователя.

        :param chat_id: int
        :param referrer_id: int
        """
        query = """
            UPDATE users
            SET referrer_id = :referrer_id
            WHERE chat_id = :chat_id
        """
        await self.connection.execute(query, {'referrer_id': referrer_id, 'chat_id': chat_id})
