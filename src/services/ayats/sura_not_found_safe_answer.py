import httpx

from app_types.stringable import Stringable
from exceptions.content_exceptions import SuraNotFoundError
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer


class SuraNotFoundSafeAnswer(TgAnswerInterface):
    """Объект обрабатывающий ошибку с не найденной сурой."""

    def __init__(self, answer: TgAnswerInterface, error_answer: TgAnswerInterface):
        self._origin = answer
        self._error_answer = error_answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except SuraNotFoundError:
            return await TgTextAnswer(
                self._error_answer,
                'Сура не найдена',
            ).build(update)
