import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgChatAction(TgAnswerInterface):
    """Запрос на API телеграма с действием.

    Используется для проверки статуса пользователя.
    """

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update) -> list[httpx.Request]:
        """Формирование запросов.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.join('sendChatAction'), headers=request.headers)
            for request in await self._origin.build(update)
        ]
