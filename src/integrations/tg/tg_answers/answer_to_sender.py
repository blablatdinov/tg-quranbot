import httpx

from app_types.stringable import Stringable
from integrations.tg.chat_id import TgChatId
from integrations.tg.tg_answers.interface import TgAnswerInterface


class TgAnswerToSender(TgAnswerInterface):
    """Ответ пользователю, от которого пришло сообщение."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Stringable) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Stringable
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(
                request.method,
                request.url.copy_add_param('chat_id', int(TgChatId(update))),
            )
            for request in await self._origin.build(update)
        ]
