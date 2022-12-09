import httpx

from app_types.stringable import Stringable
from exceptions.internal_exceptions import NotProcessableUpdateError
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgSkipNotProcessable(TgAnswerInterface):
    """Обработка и пропуск ответа, возбудившего NotProcessableUpdateError."""

    def __init__(self, answer: TgAnswerInterface):
        self._answer = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        try:
            return await self._answer.build(update)
        except NotProcessableUpdateError:
            return []
