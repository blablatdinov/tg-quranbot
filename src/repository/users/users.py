from databases import Database
from pydantic import BaseModel, parse_obj_as


class QueryResultItem(BaseModel):
    """Результат запроса."""

    chat_id: int


class UsersRepositoryInterface(object):
    """Интерфейс для работы с хранилищем множества пользователей."""

    async def get_active_user_chat_ids(self) -> list[int]:
        """Получить активных пользователей.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def update_status(self, chat_ids: list[int], to: bool):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        :param to: bool
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def increment_user_days(self, chat_ids: list[int]):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError

    async def active_users_with_city(self):
        """Вернуть активных пользователей, у которых есть город.

        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UsersRepository(UsersRepositoryInterface):
    """Класс для работы с хранилищем множества пользователей."""

    def __init__(self, connection: Database):
        self._connection = connection

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
        rows = await self._connection.fetch_all(query)
        rows = [dict(row._mapping) for row in rows]
        return [
            parsed_row.chat_id
            for parsed_row in parse_obj_as(list[QueryResultItem], rows)
        ]

    async def update_status(self, chat_ids: list[int], to: bool):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        :param to: bool
        """
        chat_ids = '({0})'.format(','.join(list(map(str, chat_ids))))
        query_template = """
            UPDATE users
            SET is_active = :to
            WHERE chat_id in {0}
        """
        query = query_template.format(chat_ids)
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
        rows = await self._connection.fetch_all(query)
        rows = [dict(row._mapping) for row in rows]
        return [
            parsed_row.chat_id
            for parsed_row in parse_obj_as(list[QueryResultItem], rows)
        ]
