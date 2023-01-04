import httpx

from app_types.stringable import Stringable
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer


class SafeFork(TgAnswerInterface):
    """Безопасный Fork."""

    def __init__(self, answer: TgAnswerInterface, message_answer: TgAnswerInterface):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param message_answer: TgAnswerInterface
        """
        self._origin = answer
        self._message_answer = message_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except NotProcessableUpdateError:
            return await TgTextAnswer(self._message_answer, 'Я не знаю как отвечать на такое сообщение').build(update)
