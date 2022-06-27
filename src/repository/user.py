from pydantic import BaseModel


class User(BaseModel):
    """Модель пользователя."""

    is_active: bool
    day: int


class UserRepositoryInterface(object):
    """Интерфейс репозитория для работы с пользователями."""

    async def create(self, chat_id: int):
        """Метод для создания пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def get(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def exists(self, chat_id: int) -> bool:
        """Метод для проверки наличия пользователя в БД.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UserRepository(UserRepositoryInterface):
    """Репозиторий для работы с пользователями."""

    def __init__(self, connection):
        self.connection = connection

    async def create(self, chat_id: int) -> int:
        """Метод для создания пользователя.

        :param chat_id: int
        """
        await self.connection.execute(
            "INSERT INTO bot_init_subscriber (tg_chat_id, is_active, day) VALUES ($1, 't', 2)", chat_id,
        )

    async def get(self, chat_id: int) -> User:
        """Метод для получения пользователя.

        :param chat_id: int
        :returns: User
        """
        query = """
            SELECT
                is_active,
                day
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
