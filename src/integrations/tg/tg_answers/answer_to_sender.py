import httpx
from loguru import logger

from integrations.tg.tg_answers.interface import TgAnswerInterface
from integrations.tg.tg_answers.update import Update


class TgAnswerToSender(TgAnswerInterface):
    """Ответ пользователю, от которого пришло сообщение."""

    def __init__(self, answer: TgAnswerInterface):
        self._origin = answer

    async def build(self, update: Update) -> list[httpx.Request]:
        """Собрать ответ.

        :param update: Update
        :return: list[httpx.Request]
        """
        return [
            httpx.Request(request.method, request.url.copy_add_param('chat_id', update.chat_id()))
            for request in await self._origin.build(update)
        ]
