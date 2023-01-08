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
import uuid
from typing import Final, Optional, Protocol, final

from databases import Database
from loguru import logger
from pydantic import BaseModel

from exceptions.base_exception import InternalBotError
from exceptions.internal_exceptions import UserNotFoundError

CHAT_ID_LITERAL: Final = 'chat_id'


@final
class User(BaseModel):
    """Модель пользователя."""

    is_active: bool
    day: int
    referrer: Optional[int] = None
    chat_id: int
    legacy_id: Optional[int] = None
    city_id: Optional[uuid.UUID]


class UserRepositoryInterface(Protocol):
    """Интерфейс репозитория для работы с пользователями."""

    async def create(self, chat_id: int, referrer_id: Optional[int] = None):
        """Метод для создания пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        """

    async def get_by_chat_id(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        """

    async def get_by_id(self, user_id: int) -> User:
        """Метод для получения пользователя.

        :param user_id: int
        """

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        """

    async def update_city(self, chat_id: int, city_id: uuid.UUID):
        """Обновить город пользователя.

        :param chat_id: int
        :param city_id: int
        """

    async def update_referrer(self, chat_id: int, referrer_id: int):
        """Обновить город пользователя.

        :param chat_id: int
        :param referrer_id: [int]
        """


@final
class UserRepository(UserRepositoryInterface):
    """Репозиторий для работы с пользователями."""

    def __init__(self, connection: Database):
        """Конструктор класса.

        :param connection: Database
        """
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
        query_return_value = await self.connection.fetch_one(
            query,
            {CHAT_ID_LITERAL: chat_id, 'referrer_id': referrer_id},
        )
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
        record = await self.connection.fetch_one(query, {CHAT_ID_LITERAL: chat_id})
        if not record:
            raise UserNotFoundError('Пользователь с chat_id: {0} не найден'.format(chat_id))
        return User.parse_obj(dict(record._mapping))  # noqa: WPS437

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :returns: bool
        """
        query = 'SELECT COUNT(*) FROM users WHERE chat_id = :chat_id'
        count = await self.connection.fetch_val(query, {CHAT_ID_LITERAL: chat_id})
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
        await self.connection.execute(query, {'city_id': str(city_id), CHAT_ID_LITERAL: chat_id})

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
        await self.connection.execute(query, {'referrer_id': referrer_id, CHAT_ID_LITERAL: chat_id})

    async def get_by_id(self, user_id: int) -> User:
        """Метод для получения пользователя.

        :param user_id: int
        :raises UserNotFoundError: if user not found
        :return: User
        """
        query = """
            SELECT
                chat_id,
                is_active,
                day,
                referrer_id as referrer,
                city_id
            FROM users WHERE legacy_id = :user_id
        """
        row = await self.connection.fetch_one(query, {'user_id': user_id})
        if not row:
            raise UserNotFoundError('Пользователь с legacy_id: {0} не найден'.format(user_id))
        return User.parse_obj(row._mapping)  # noqa: WPS437
