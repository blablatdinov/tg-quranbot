import httpx

from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer
from integrations.tg.tg_answers.update import Update


class SafeFork(TgAnswerInterface):
    """Безопасный Fork."""

    def __init__(self, answer: TgAnswerInterface, message_answer: TgAnswerInterface):
        self._origin = answer
        self._message_answer = message_answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except NotProcessableUpdateError:
            return await TgTextAnswer(self._message_answer, 'Я не знаю как отвечать на такое сообщение').build(update)
