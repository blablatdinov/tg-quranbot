from contextlib import suppress

import httpx

from app_types.stringable import Stringable
from exceptions.user import UserAlreadyActive, UserAlreadyExists
from integrations.nats_integration import SinkInterface
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer
from integrations.tg.tg_datetime import TgDateTime
from repository.users.user import UserRepositoryInterface
from repository.users.users import UsersRepositoryInterface


class UserAlreadyExistsAnswer(TgAnswerInterface):
    """Декоратор обработчика стартового сообщение с предохранением от UserAlreadyExists."""

    def __init__(
        self,
        start_answer: TgAnswerInterface,
        sender_answer: TgAnswerInterface,
        user_repo: UserRepositoryInterface,
        users_repo: UsersRepositoryInterface,
        event_sink: SinkInterface,
    ):
        """Конструктор класса.

        :param start_answer: TgAnswerInterface
        :param sender_answer: TgAnswerInterface
        :param user_repo: UserRepositoryInterface
        :param users_repo: UsersRepositoryInterface
        :param event_sink: SinkInterface
        """
        self._origin = start_answer
        self._user_repo = user_repo
        self._sender_answer = sender_answer
        self._users_repo = users_repo
        self._event_sink = event_sink

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        :raises UserAlreadyActive: if user already active
        """
        with suppress(UserAlreadyExists):
            return await self._origin.build(update)
        user = await self._user_repo.get_by_chat_id(int(TgChatId(update)))
        if user.is_active:
            raise UserAlreadyActive
        await self._users_repo.update_status([int(TgChatId(update))], to=True)
        await self._event_sink.send(
            {
                'user_id': int(TgChatId(update)),
                'date_time': TgDateTime(update).datetime(),
            },
            'User.Reactivated',
            1,
        )
        return await TgTextAnswer(
            self._sender_answer,
            'Рады видеть вас снова, вы продолжите с дня {0}'.format(user.day),
        ).build(update)
