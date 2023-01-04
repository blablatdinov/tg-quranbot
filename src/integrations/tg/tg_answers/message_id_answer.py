import httpx

from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgMessageIdAnswer(TgAnswerInterface):
    """Ответ с идентификатором сообщения."""

    def __init__(self, answer: TgAnswerInterface, message_id: int):
        """Конструктор класса.

        :param answer: TgAnswerInterface
        :param message_id: int
        """
        self._origin = answer
        self._message_id = message_id

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('message_id', self._message_id),
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
