import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgKeyboardEditAnswer(TgAnswerInterface):
    """Ответ с отредактированной клавиатурой."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update) -> list[httpx.Request]:
        """Пересобрать запросы к API к телеграмма.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.join('editMessageReplyMarkup'),
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
