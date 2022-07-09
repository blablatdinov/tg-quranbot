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
