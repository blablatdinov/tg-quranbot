import httpx

from app_types.stringable import Stringable
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgLocationAnswer(TgAnswerInterface):
    """Ответ на присланную геопозицию."""

    def __init__(self, answer: TgAnswerInterface):
        self._answer = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            update.message().location()
        except AttributeError:
            return []
        return await self._answer.build(update)
