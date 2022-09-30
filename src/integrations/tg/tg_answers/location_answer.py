import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgLocationAnswer(TgAnswerInterface):
    """Ответ на присланную геопозицию."""

    def __init__(self, answer: TgAnswerInterface):
        self._answer = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        try:
            update.message().location()
        except AttributeError:
            return []
        return await self._answer.build(update)
