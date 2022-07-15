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
