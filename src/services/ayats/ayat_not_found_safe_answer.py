import httpx

from exceptions.content_exceptions import AyatNotFoundError
from integrations.tg.tg_answers import TgAnswerInterface, TgTextAnswer
from integrations.tg.tg_answers.update import Update


class AyatNotFoundSafeAnswer(TgAnswerInterface):
    """Объект обрабатывающий ошибку с не найденным аятом."""

    def __init__(self, answer: TgAnswerInterface, error_answer: TgAnswerInterface):
        self._origin = answer
        self._error_answer = error_answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :returns: list[httpx.Request]
        """
        try:
            return await self._origin.build(update)
        except AyatNotFoundError:
            return await TgTextAnswer(
                self._error_answer,
                'Аят не найден',
            ).build(update)
