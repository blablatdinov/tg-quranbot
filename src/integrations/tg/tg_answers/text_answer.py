import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgTextAnswer(TgAnswerInterface):
    """Ответ пользователю с текстом."""

    def __init__(self, answer: TgAnswerInterface, text: str):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param text: str
        """
        self._origin = answer
        self._text = text

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.copy_add_param('text', self._text))
            for request in await self._origin.build(update)
        ]
