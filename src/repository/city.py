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
from typing import Protocol, final

from databases import Database
from pydantic import BaseModel, parse_obj_as


@final
class City(BaseModel):
    """Модель города."""

    id: uuid.UUID
    name: str


class CityRepositoryInterface(Protocol):
    """Интерфейс репозитория городов."""

    async def search_by_name(self, query: str) -> list[City]:
        """Поиск по имени.

        :param query: str
        """


@final
class CityRepository(CityRepositoryInterface):
    """Класс для работы с городами в БД."""

    def __init__(self, connection: Database):
        """Конструктор класса.

        :param connection: Database
        """
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
