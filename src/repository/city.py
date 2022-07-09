import abc

from pydantic import BaseModel


class City(BaseModel):
    """Модель города."""

    id: int
    name: str


class CityRepositoryInterface(object):
    """Интерфейс репозитория городов."""

    @abc.abstractmethod
    async def search_by_name(self, query: str):
        """Поиск по имени.

        :param query: str
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def search_by_variants(self, query_variants: list[str]) -> list[City]:
        """Поиск по нескольким вариантам имен.

        :param query_variants: list[str]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class CityRepository(CityRepositoryInterface):
    """Класс для работы с городами в БД."""

    def __init__(self, connection):
        self.connection = connection

    async def search_by_name(self, search_query: str) -> list[City]:
        """Поиск по имени.

        :param search_query: str
        :returns: list[City]
        """
        search_query = '%{0}%'.format(search_query)
        query = 'SELECT id, name FROM prayer_city WHERE name ILIKE $1'
        rows = await self.connection.fetch(query, search_query)
        return [
            City(**dict(row))
            for row in rows
        ]

    async def search_by_variants(self, query_variants: list[str]) -> list[City]:
        """Поиск по нескольким вариантам имен.

        :param query_variants: list[str]
        :returns: list[City]
        """
        # FIXME: using ILIKE IN
        # FIXME: remove noqa
        search_query = ' or '.join(["name ILIKE '%{0}%'".format(query_variant) for query_variant in query_variants])
        query = 'SELECT id, name FROM prayer_city WHERE {0}'.format(search_query)  # noqa: S608
        rows = await self.connection.fetch(query)
        return [
            City(**dict(row))
            for row in rows
        ]
