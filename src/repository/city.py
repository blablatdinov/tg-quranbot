import abc
import uuid

from databases import Database
from pydantic import BaseModel, parse_obj_as


class City(BaseModel):
    """Модель города."""

    id: uuid.UUID
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

    def __init__(self, connection: Database):
        self._connection = connection

    async def search_by_name(self, search_query: str) -> list[City]:
        """Поиск по имени.

        :param search_query: str
        :returns: list[City]
        """
        search_query = '%{0}%'.format(search_query)
        query = 'SELECT city_id AS id, name FROM cities WHERE name ILIKE :search_query'
        rows = await self._connection.fetch_all(query, {'search_query': search_query})
        return parse_obj_as(list[City], [row._mapping for row in rows])  # noqa: WPS437
