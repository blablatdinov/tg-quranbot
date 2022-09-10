import httpx

from services.tg_answers.interface import TgAnswerInterface


class TgChatIdAnswer(TgAnswerInterface):
    """Ответ пользователю на конкретный идентификатор чата."""

    def __init__(self, answer: TgAnswerInterface, chat_id: int):
        self._origin = answer
        self._chat_id = chat_id

    async def build(self, update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('chat_id', self._chat_id),
                stream=request.stream,
                headers=request.headers,
            )
            for request in await self._origin.build(update)
        ]
