import abc

from asyncpg import Connection
from pydantic import BaseModel, parse_obj_as


class City(BaseModel):
    """Модель города."""

    id: int
    name: str


class CityRepositoryInterface(object):
    """Интерфейс репозитория городов."""

    @abc.abstractmethod
    async def search_by_name(self, query: str) -> list[City]:
        """Поиск по имени.

        :param query: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_user_city_by_chat_id(self, chat_id: int) -> City:
        """Доастать город для пользователя.

        :param chat_id: int
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class CityRepository(CityRepositoryInterface):
    """Класс для работы с городами в БД."""

    def __init__(self, connection: Connection):
        self.connection = connection

    async def search_by_name(self, search_query: str) -> list[City]:
        """Поиск по имени.

        :param search_query: str
        :returns: list[City]
        """
        search_query = '%{0}%'.format(search_query)
        query = 'SELECT id, name FROM prayer_city WHERE name ILIKE $1'
        rows = await self.connection.fetch(query, search_query)
        return parse_obj_as(list[City], rows)

    async def get_user_city_by_chat_id(self, chat_id: int) -> City:
        """Доастать город для пользователя.

        :param chat_id: int
        :return: City
        """
        query = """
            SELECT
                c.id,
                c.name
            FROM prayer_city c
            INNER JOIN bot_init_subscriber s ON c.id = s.city_id
            WHERE s.tg_chat_id = $1
        """
        row = await self.connection.fetchrow(query, chat_id)
        return City.parse_obj(row)
