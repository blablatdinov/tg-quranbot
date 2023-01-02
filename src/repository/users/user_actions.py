import datetime
import enum
from typing import Protocol

import pytz
from asyncpg import Connection
from pydantic import BaseModel


class UserActionEnum(str, enum.Enum):  # noqa: WPS600
    """Типы действий пользователя."""

    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBED = 'unsubscribed'
    REACTIVATED = 'reactivated'


class UserAction(BaseModel):
    """Модель действия пользователя."""

    date_time: datetime.datetime
    action: UserActionEnum
    chat_id: int


class UserActionRepositoryInterface(Protocol):
    """Интерфейс к хранилищу действий пользователя."""

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        """Создать действие пользователя.

        :param chat_id: int
        :param action: UserActionEnum
        """


class UserActionRepository(UserActionRepositoryInterface):
    """Класс для работы с действиями пользователя в БД."""

    def __init__(self, connection: Connection):
        self.connection = connection

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        """Создать действие пользователя.

        :param chat_id: int
        :param action: UserActionEnum
        """
        query = """
            INSERT INTO
            bot_init_subscriberaction
            (_date_time, action, subscriber_id)
            VALUES
            ($1, $2, (SELECT id FROM bot_init_subscriber WHERE tg_chat_id = $3))
        """
        await self.connection.execute(
            query,
            datetime.datetime.now(pytz.timezone('Europe/Moscow')),
            action,
            chat_id,
        )
