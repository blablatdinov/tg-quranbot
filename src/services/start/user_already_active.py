import httpx

from app_types.stringable import Stringable
from exceptions.user import UserAlreadyActive
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer


class UserAlreadyActiveSafeAnswer(TgAnswerInterface):
    """Ответ для случаев когда пользователь уже активен."""

    def __init__(self, answer: TgAnswerInterface, sender_answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param sender_answer: TgAnswerInterface
        """
        self._origin = answer
        self._sender_answer = sender_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Сборка ответа.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except UserAlreadyActive:
            return await TgTextAnswer(
                self._sender_answer,
                'Вы уже зарегистрированы!',
            ).build(update)
