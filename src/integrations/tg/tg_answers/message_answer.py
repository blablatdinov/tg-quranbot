import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgMessageAnswer(TgAnswerInterface):
    """Текстовое сообщение."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update) -> list[httpx.Request]:
        """Формирование запросов.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.join('sendMessage'))
            for request in await self._origin.build(update)
        ]
