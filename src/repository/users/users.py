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
from typing import Protocol, final

import attrs
from databases import Database
from pydantic import BaseModel, parse_obj_as


@final
class QueryResultItem(BaseModel):
    """Результат запроса."""

    chat_id: int


class UsersRepositoryInterface(Protocol):
    """Интерфейс для работы с хранилищем множества пользователей."""

    async def get_active_user_chat_ids(self) -> list[int]:
        """Получить активных пользователей."""

    async def update_status(self, chat_ids: list[int], to: bool):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        :param to: bool
        """

    async def increment_user_days(self, chat_ids: list[int]):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        """

    async def active_users_with_city(self) -> list[int]:
        """Вернуть активных пользователей, у которых есть город."""


@final
@attrs.define
class UsersRepository(UsersRepositoryInterface):
    """Класс для работы с хранилищем множества пользователей."""

    _connection: Database

    async def get_active_user_chat_ids(self) -> list[int]:
        """Получить активных пользователей.

        :returns: list[User]
        """
        query = """
            SELECT
                chat_id
            FROM users
            WHERE is_active = 't'
        """
        db_rows = await self._connection.fetch_all(query)
        rows = [dict(row._mapping) for row in db_rows]  # noqa: WPS437
        return [
            parsed_row.chat_id
            for parsed_row in parse_obj_as(list[QueryResultItem], rows)
        ]

    async def update_status(self, chat_ids: list[int], to: bool):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        :param to: bool
        """
        if not chat_ids:
            return
        chat_ids_for_query = '({0})'.format(','.join(list(map(str, chat_ids))))
        query_template = """
            UPDATE users
            SET is_active = :to
            WHERE chat_id in {0}
        """
        query = query_template.format(chat_ids_for_query)
        await self._connection.execute(query, {'to': to})

    async def increment_user_days(self, chat_ids: list[int]):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        """
        query_template = """
            UPDATE users
            SET day = day + 1
            WHERE chat_id in ({0})
        """
        query = query_template.format(','.join(map(str, chat_ids)))
        await self._connection.execute(query)

    async def active_users_with_city(self) -> list[int]:
        """Вернуть активных пользователей, у которых есть город.

        :return: list[int]
        """
        query = """
            SELECT chat_id as chat_id
            FROM users s
            INNER JOIN cities c on s.city_id = c.city_id
            WHERE s.is_active = 't'
            ORDER BY chat_id
        """
        db_rows = await self._connection.fetch_all(query)
        rows = [dict(row._mapping) for row in db_rows]  # noqa: WPS437
        return [
            parsed_row.chat_id
            for parsed_row in parse_obj_as(list[QueryResultItem], rows)
        ]
