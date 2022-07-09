import abc
from dataclasses import dataclass

from pydantic import BaseModel


class City(BaseModel):

    id: int
    name: str


class CityRepositoryInterface(object):

    @abc.abstractmethod
    async def search_by_name(self, query: str):
        raise NotImplementedError

    @abc.abstractmethod
    async def search_by_variants(self, query_variants: list[str]) -> list[City]:
        raise NotImplementedError


class CityRepository(CityRepositoryInterface):

    def __init__(self, connection):
        self.connection = connection

    async def search_by_name(self, search_query: str):
        search_query = '%{0}%'.format(search_query)
        query = "SELECT id, name FROM prayer_city WHERE name ILIKE $1"
        rows = await self.connection.fetch(query, search_query)
        return [
            City(**dict(row))
            for row in rows
        ]

    async def search_by_variants(self, query_variants: list[str]) -> list[City]:
        # FIXME: using ILIKE IN
        search_query = ' or '.join([f"name ILIKE '%{x}%'" for x in query_variants])
        query = "SELECT id, name FROM prayer_city WHERE {0}".format(search_query)
        rows = await self.connection.fetch(query)
        return [
            City(**dict(row))
            for row in rows
        ]
