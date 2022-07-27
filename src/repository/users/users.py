from asyncpg import Connection
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


class UsersRepository(UsersRepositoryInterface):
    """Класс для работы с хранилищем множества пользователей."""

    def __init__(self, connection: Connection):
        self._connection = connection

    async def get_active_user_chat_ids(self) -> list[int]:
        """Получить активных пользователей.

        :returns: list[User]
        """
        query = """
            SELECT
                tg_chat_id as chat_id
            FROM bot_init_subscriber
            WHERE is_active = 't'
        """
        rows = await self._connection.fetch(query)
        return [
            parsed_row.chat_id
            for parsed_row in parse_obj_as(list[QueryResultItem], rows)
        ]

    async def update_status(self, chat_ids: list[int], to: bool):
        """Обнвоить статус пользователей.

        :param chat_ids: list[int]
        :param to: bool
        """
        placeholders_list = ','.join(
            [
                '${0}'.format(str(placeholder_num))
                for placeholder_num in range(2, len(chat_ids) + 2)
            ],
        )
        query_template = """
            UPDATE bot_init_subscriber
            SET is_active = $1
            WHERE tg_chat_id in ({0})
        """
        query = query_template.format(placeholders_list)
        await self._connection.execute(query, to, *chat_ids)
