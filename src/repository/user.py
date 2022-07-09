from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """Модель пользователя."""

    id: int
    is_active: bool
    day: int
    referrer: Optional[int] = None
    chat_id: int
    city_id: Optional[int]


class UserRepositoryInterface(object):
    """Интерфейс репозитория для работы с пользователями."""

    async def create(self, chat_id: int, referrer_id: Optional[int]):
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

    async def active_users(self):
        """Получить активных пользователей.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def update_city(self, chat_id: int, city_id: int):
        """Обновить город пользователя.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError



class UserRepository(UserRepositoryInterface):
    """Репозиторий для работы с пользователями."""

    def __init__(self, connection):
        self.connection = connection

    async def create(self, chat_id: int, referrer_id: Optional[int]):
        """Метод для создания пользователя.

        :param chat_id: int
        :param referrer_id: Optional[int]
        """
        await self.connection.execute(
            "INSERT INTO bot_init_subscriber (tg_chat_id, is_active, day, referer_id) VALUES ($1, 't', 2, $2)",
            chat_id,
            referrer_id,
        )

    async def get_by_chat_id(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :returns: User
        """
        query = """
            SELECT
                id,
                is_active,
                day,
                referer_id as referrer,
                tg_chat_id as chat_id,
                city_id
            FROM bot_init_subscriber
            WHERE tg_chat_id = $1
        """
        record = await self.connection.fetchrow(query, chat_id)
        return User(**dict(record))

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :returns: bool
        """
        query = 'SELECT COUNT(*) FROM bot_init_subscriber WHERE tg_chat_id = $1'
        record = await self.connection.fetchrow(query, chat_id)
        return bool(record['count'])

    async def active_users(self) -> list[User]:
        """Получить активных пользователей.

        :returns: list[User]
        """
        query = """
            SELECT
                id,
                is_active,
                day,
                referer_id as referrer,
                tg_chat_id as chat_id,
                city_id
            FROM bot_init_subscriber
            WHERE is_active = 't'
        """
        rows = await self.connection.fetch(query)
        return [
            User(**dict(row))
            for row in rows
        ]

    async def update_city(self, chat_id: int, city_id: int):
        """Обновить город пользователя.

        """
        query = """
            UPDATE bot_init_subscriber
            SET city_id = $1
            WHERE tg_chat_id = $2
        """
        print(f'{chat_id=}', f'{city_id=}')
        await self.connection.execute(query, city_id, chat_id)
