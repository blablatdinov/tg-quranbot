import datetime
import enum

from pydantic import BaseModel


class UserActionEnum(str, enum.Enum):
    SUBSCRIBED = 'subscribed'
    UNSUBSCRIBED = 'unsubscribed'
    REACTIVATED = 'reactivated'


class UserAction(BaseModel):

    date_time: datetime.datetime
    action: UserActionEnum
    chat_id: int


class UserActionRepositoryInterface(object):

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        """Создать действие пользователя.

        :param chat_id: int
        :param action: UserActionEnum
        :raises NotImplementedError: if not implemented
        """
        raise NotImplementedError


class UserActionRepository(UserActionRepositoryInterface):

    def __init__(self, connection):
        self.connection = connection

    async def create_user_action(self, chat_id: int, action: UserActionEnum):
        """Создать действие пользователя.

        :param chat_id: int
        :param action: UserActionEnum
        """
        query = """
            INSERT INTO
            bot_init_subscriberaction
            (date_time, action, subscriber_id)
            VALUES
            ($1, $2, (SELECT id FROM bot_init_subscriber WHERE tg_chat_id = $3))
        """
        await self.connection(query, datetime.datetime.now(), action, chat_id)
