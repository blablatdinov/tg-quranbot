import httpx

from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgSkipNotProcessable(TgAnswerInterface):

    def __init__(self, answer: TgAnswerInterface):
        self._answer = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            return await self._answer.build(update)
        except NotProcessableUpdateError:
            return []
